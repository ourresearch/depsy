import re
from time import time
import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import sql
from validate_email import validate_email
from lxml import html
import requests

from app import db

from jobs import update_registry
from jobs import Update
from models.person import get_or_make_person
from models.package import Package
from models.github_repo import GithubRepo
from models import github_api
from models.byline import Byline
from models.academic import is_academic_phrase
from util import elapsed
from util import truncate
from collections import defaultdict

class CranPackage(Package):
    class_host = "cran"

    __mapper_args__ = {
        'polymorphic_identity': 'cran'
    }

    def __repr__(self):
        return u'<CranPackage {name}>'.format(
            name=self.id)

    @property
    def language(self):
        return "r"

    @property
    def host_url(self):
        return "https://cran.r-project.org/web/packages/{}".format(self.project_name)


    @property
    def pagerank_max(self):
        return 0.0601950151409884823  # brings lowest up to about 0

    @property
    def pagerank_99th(self):
        return 0.000188688596986499657  #95 percentile actually

    @property
    def pagerank_min(self):
        return 0.00001166849

    @property
    def num_downloads_max(self):
        return 161454  # brings lowest up to about 0

    @property
    def num_downloads_99th(self):
        return 40846  # 99th percentile

    @property
    def num_downloads_median(self):
        return 285.0  # 99th percentile


    @property
    def num_citations_99th(self):
        return 189

    @property
    def num_citations_max(self):
        return 2799  # brings lowest up to about 0


    def refresh(self):
        self.set_is_academic()
        self.set_cran_about()
        self.set_summary()
        self.set_num_downloads()
        self.set_github_repo()
        self.set_proxy_papers()

        self.save_all_people()  #includes save_host_contributors
        # self.set_github_repo_ids() # not sure if we use this anymore?
        self.set_tags()

        self.set_credit()

        self.set_num_downloads()
        self.set_num_citations()
        self.set_host_reverse_depends()

        self.updated = datetime.datetime.utcnow()


    def set_summary(self):
        self.summary = "A nifty project."
        try:
            self.summary = truncate(self.api_raw["Description"])
        except (KeyError, TypeError):
            pass

    def set_is_academic(self):
        self.is_academic = True

    def save_host_contributors(self):
        if not self.api_raw:
            return

        raw_byline_string = self.api_raw["Author"]
        maintainer = self.api_raw["Maintainer"]

        byline = Byline(raw_byline_string)

        extracted_name_dicts = byline.author_email_pairs()

        for kwargs_dict in extracted_name_dicts:
            person = get_or_make_person(**kwargs_dict)
            self._save_contribution(person, "author")


    def set_github_repo_ids(self):
        q = db.session.query(GithubRepo.login, GithubRepo.repo_name)
        q = q.filter(GithubRepo.language == 'r')
        q = q.filter(GithubRepo.login != 'cran')  # these are just mirrors.
        q = q.filter(GithubRepo.bucket.contains({"cran_descr_file_name": self.project_name}))
        q = q.order_by(GithubRepo.api_raw['stargazers_count'].cast(db.Integer).desc())

        start = time()
        row = q.first()
        print "Github repo query took {}".format(elapsed(start, 4))

        if row is None:
            return None

        else:
            print "Setting a new github repo for {}: {}/{}".format(
                self,
                row[0],
                row[1]
            )
            self.github_owner = row[0]
            self.github_repo_name = row[1]
            self.bucket["matched_from_github_metadata"] = True




    def set_tags(self):
        url_template = "https://cran.r-project.org/web/packages/{}/"
        url = url_template.format(self.project_name)

        requests.packages.urllib3.disable_warnings()  
        response = requests.get(url)
        tags = []
        if "views" in response.text:
            page = response.text
            page = page.replace("&nbsp;", " ")  # otherwise starts-with for lxml doesn't work
            tree = html.fromstring(page)
            data = {}
            tags_raw = tree.xpath('//tr[(starts-with(td[1], "In views"))]/td[2]/a/text()')
            for tag in tags_raw:
                tag = tag.strip()
                tag = tag.strip('"')
                tags.append(tag.lower())
        print "returning tags", tags
        self.tags = tags


    def distinctiveness_query_prefix(self, source):
        if source.__class__.__name__ == "Pmc":
            return '("r package" OR "r statistical") AND '
        elif source.__class__.__name__ == "Ads":
            return '(="r package" OR ="r statistical") AND '


    def set_cran_about(self):
        url_template = "http://crandb.r-pkg.org/%s"
        data_url = url_template % self.project_name
        print data_url
        response = requests.get(data_url)
        self.api_raw = response.json()


    def set_num_downloads(self):

        date_one_month_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)

        url_template = "http://cranlogs.r-pkg.org/downloads/daily/1900-01-01:2020-01-01/%s"
        data_url = url_template % self.project_name
        print data_url
        response = requests.get(data_url)
        if "day" in response.text:
            data = {}
            all_days = response.json()[0]["downloads"]
            # data["total_downloads"] = sum([int(day["downloads"]) for day in all_days])
            # data["first_download"] = min([day["day"] for day in all_days])
            data["daily_downloads"] = all_days
        else:
            data = {"total_downloads": 0}

        # now get the ones in the last month
        download_sum = 0
        for download_dict in data.get("daily_downloads", []):
            if download_dict["day"] > date_one_month_ago.isoformat():
                download_sum += download_dict["downloads"]

        self.num_downloads = download_sum



    def set_github_repo(self):
        try:
            urls_str = self.api_raw['URL']
        except KeyError:
            return False

        # People put all kinds of lists in this field. So we're splitting on
        # newlines, commas, and spaces. Won't get everything, but will
        # get most.
        urls = re.compile(r",*\s*\n*").split(urls_str)

        for url in urls:
            login, repo_name = github_api.login_and_repo_name_from_url(url)
            if login and repo_name:
                self.github_repo_name = repo_name
                self.github_owner = login

                # there may be more than one github url. if so, too bad,
                # we're just picking the first one.
                break

        print u"successfully set a github ID for {name}: {login}/{repo_name}.".format(
            name=self.project_name,
            login=self.github_owner,
            repo_name=self.github_repo_name
        )


    def set_host_reverse_depends(self):
        url_template = "https://cran.r-project.org/web/packages/%s/"
        data_url = url_template % self.project_name
        print data_url

        # this call keeps timing out for some reason.  quick workaround:
        response = None
        while not response:
            try:
                response = requests.get(data_url)
            except requests.exceptions.ConnectionError:
                # try again
                print "connection timed out, trying again"
                pass

        if "Reverse" in response.text:
            page = response.text
            page = page.replace("&nbsp;", " ")  # otherwise starts-with for lxml doesn't work
            tree = html.fromstring(page)
            data = {}
            data["reverse_imports"] = tree.xpath('//tr[(starts-with(td[1], "Reverse imports"))]/td[2]/a/text()')
            data["reverse_depends"] = tree.xpath('//tr[(starts-with(td[1], "Reverse depends"))]/td[2]/a/text()')
            data["reverse_suggests"] = tree.xpath('//tr[(starts-with(td[1], "Reverse suggests"))]/td[2]/a/text()')
            data["reverse_enhances"] = tree.xpath('//tr[(starts-with(td[1], "Reverse enhances"))]/td[2]/a/text()')
            all_reverse_deps = set(data["reverse_imports"] + data["reverse_depends"] + data["reverse_suggests"] + data["reverse_enhances"])
            data["all_reverse_deps"] = list(all_reverse_deps)

        else:
            data = {"all_reverse_deps": []}

        self.host_reverse_deps = []
        for dep_kind in ["reverse_depends", "reverse_imports"]:
            if dep_kind in data:
                self.host_reverse_deps += data[dep_kind]


    def set_proxy_papers(self):
        url_template = "https://cran.r-project.org/web/packages/%s/citation.html"
        data_url = url_template % self.project_name
        print data_url

        response = requests.get(data_url, timeout=30)

        if response and response.status_code==200 and "<pre>" in response.text:
            page = response.text
            tree = html.fromstring(page)
            proxy_papers = str(tree.xpath('//pre/text()'))
            print "found proxy paper!"
            # print proxy_papers
        else:
            print "no proxy paper found"
            proxy_papers = "No proxy paper"

        self.proxy_papers = proxy_papers




