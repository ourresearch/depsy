import re
from time import time

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
from models.byline import Byline
from models.academic import is_academic_phrase
from util import elapsed
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
    def pagerank_offset_to_recenter_scores(self):
        # select log(1.0/max(pagerank)), host from package group by host
        # min pagerank = 
        return 3.08  # brings lowest up to about 0

    @property
    def num_citations_offset_to_recenter_scores(self):
        # select log(1.0/max(num_citations)), host from package group by host        
        return 3.45  # brings lowest up to about 0

    @property
    def pagerank_max(self):
        return 0.0601950151409884823  # brings lowest up to about 0

    @property
    def pagerank_99th(self):
        return 0.00139519528585026371 # 99th percentile

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
    def num_citations_max(self):
        return 2799  # brings lowest up to about 0


    def save_host_contributors(self):
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


    def set_num_downloads_since(self):

        ### hacky!  hard code this
        get_downloads_since_date = "2015-07-25"

        if not self.num_downloads:
            return None

        download_sum = 0

        for download_dict in self.downloads.get("daily_downloads", []):
            if download_dict["day"] > get_downloads_since_date:
                download_sum += download_dict["downloads"]

        self.downloads["last_month"] = download_sum



    def set_host_reverse_deps(self):
        self.host_reverse_deps = []
        for dep_kind in ["reverse_depends", "reverse_imports"]:
            if dep_kind in self.all_r_reverse_deps:
                self.host_reverse_deps += self.all_r_reverse_deps[dep_kind]


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

    @property
    def distinctiveness_query_prefix(self):
        return '(="r package" OR ="r statistical") AND '


    @property
    def impact_rank_max(self):
        # get these with this sql:
            # select count(id) from package where host='cran'
        return 7057

    def set_is_academic(self):
        self.is_academic = False

        # skip tags for cran, because they are tasks and don't work well here

        # if you have an academic-sounding name, you're academic
        if is_academic_phrase(self.project_name):
            self.is_academic = True

        # if you have an academic-sounding summary, you're academic
        if is_academic_phrase(self.summary):
            self.is_academic = True

        # if you have an academic-sounding cran description, you're academic
        try:
            if is_academic_phrase(self.api_raw["Description"]):
                self.is_academic = True
        except KeyError:
            pass

        # check proxy paper type
        sciency_proxy_paper_types = [
            '@Book', 
            '@InBook',
            '@InPhdThesis',
            '@PhdThesis',
            '@Article',
            '@InProceedings'
            # '%@InCollection%'
            # '%@Manual%'
            # '%@Misc%'
            # '%@Unpublished%'
            # '%@TechReport%'
        ]

        for proxy_paper_type in sciency_proxy_paper_types:
            if proxy_paper_type in self.proxy_papers:
                print "setting is_academic=True due to proxy paper type"
                self.is_academic = True

        return self.is_academic


