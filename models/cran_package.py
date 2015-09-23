from app import db
from sqlalchemy.dialects.postgresql import JSONB
from time import time
from validate_email import validate_email
import re
from jobs import update_registry
from jobs import Update

from models.person import get_or_make_person
from models.package import Package
from models.github_repo import GithubRepo
from util import elapsed


class CranPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'cran'
    }

    def __repr__(self):
        return u'<CranPackage {name}>'.format(
            name=self.id)

    def _return_clean_author_string(self, all_authors):
        # print "all authors before:", all_authors

        halt_patterns = [" punt ", " adapted ", " comply "]
        for pattern in halt_patterns:
            if pattern in all_authors:
                return None

        remove_patterns = [
            "\(.*?\)",
            "\[.*?\]",
            "with.*$",
            "assistance.*$",
            "contributions.*$",
            "under.*$",
            "and others.*$",
            "and many others.*$",
            "and authors.*$",
            "assisted.*$"
        ]
        for pattern in remove_patterns:
            all_authors = re.sub(pattern, "", all_authors)
            # print pattern, all_authors

        all_authors = all_authors.replace("<U+000a>", " ")
        all_authors = all_authors.replace("\n", " ")
        all_authors = all_authors.replace(" & ", ",")
        all_authors = all_authors.replace(" and ", ",")
        all_authors.strip(" .")
        # print "all authors after:", all_authors
        return all_authors

    def save_host_contributors(self):
        all_authors = self.api_raw["Author"]
        maintainer = self.api_raw["Maintainer"]

        print "starting with all_authors", all_authors
        clean_author_string = self._return_clean_author_string(all_authors)
        if not clean_author_string:
            return None

        author_parts = clean_author_string.split(",")
        author_name = None
        author_email = None
        for clean_part in author_parts:
            # print "clean_part", clean_part
            if "<" in clean_part:
                match = re.search(ur"(.*)(?:\w*\<(.*)\>)", clean_part)
                if match:
                    author_name = match.group(0)
                    author_email = match.group(1)
                else:
                    print u"no email match on", clean_part
            else:
                author_name = clean_part

            if author_name:
                author_name = author_name.strip()
                if author_email and validate_email(author_email):
                   person = get_or_make_person(name=author_name, email=author_email)
                else:
                   person = get_or_make_person(name=author_name)
                print u"saving person {}".format(person)
                self._save_contribution(person, "author")






    def _remove_all_authors_cruft(self, all_authors):
        return all_authors

    def _extract_author_strings(self, all_authors):
        return []

    def _name_and_email_from_author_str(self, author_str):
        return [None, None]


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

    @property
    def as_snippet(self):
        ret = self._as_package_snippet
        ret["language"] = "r"
        return ret


    def set_host_reverse_deps(self):
        self.host_reverse_deps = []
        for dep_kind in ["reverse_depends", "reverse_imports"]:
            if dep_kind in self.all_r_reverse_deps:
                self.host_reverse_deps += self.all_r_reverse_deps[dep_kind]
















########################################################################

# update functions

########################################################################


q = db.session.query(CranPackage.id)
q = q.filter(~CranPackage.downloads.has_key('last_month'))

update_registry.register(Update(
    job=CranPackage.set_num_downloads_since,
    query=q,
    queue_id=7
))







q = db.session.query(CranPackage.id)
update_registry.register(Update(
    job=CranPackage.set_host_reverse_deps,
    query=q,
    queue_id=8
))


q = db.session.query(CranPackage.id)
update_registry.register(Update(
    job=CranPackage.save_host_contributors,
    query=q,
    queue_id=8
))








