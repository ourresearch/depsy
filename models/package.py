from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import deferred

from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import func
from util import elapsed
from time import time
from validate_email import validate_email

from models import github_api
from models.person import Person
from models.person import get_or_make_person
from models.contribution import Contribution
from models.github_repo import GithubRepo
from jobs import enqueue_jobs

class Package(db.Model):
    full_name = db.Column(db.Text, primary_key=True)
    host = db.Column(db.Text)
    project_name = db.Column(db.Text)

    github_owner = db.Column(db.Text)
    github_repo_name = db.Column(db.Text)

    api_raw = deferred(db.Column(JSONB))
    downloads = db.Column(JSONB)

    github_reverse_deps = db.Column(JSONB)
    host_reverse_deps = db.Column(JSONB)
    dependencies = db.Column(JSONB)

    proxy_papers = db.Column(db.Text)
    github_contributors = db.Column(JSONB)
    bucket = db.Column(MutableDict.as_mutable(JSONB))

    contributions = db.relationship(
        'Contribution',
        lazy='subquery',
        cascade="all, delete-orphan",
        backref=db.backref("package", lazy="subquery")
    )
    __mapper_args__ = {
        'polymorphic_on': host,
        'with_polymorphic': '*'
    }


    def __repr__(self):
        return u'<Package {name}>'.format(
            name=self.full_name)

    @classmethod
    def valid_package_names(cls, module_names):
        """
        this will normally be called by subclasses, to filter by specific package hosts
        """
        lowercase_module_names = [n.lower() for n in module_names]
        q = db.session.query(cls.project_name)
        q = q.filter(func.lower(cls.project_name).in_(lowercase_module_names))
        response = [row[0] for row in q.all()]
        return response

    def save_github_owners_and_contributors(self):
        self.save_github_contribs_to_db()
        self.save_github_owner_to_db()

    def save_host_contributors(self):
        # this needs to be overridden, because it depends on whether we've
        # got a pypi or cran package...they have diff metadata formats.
        raise NotImplementedError

    def save_github_contribs_to_db(self):
        if isinstance(self.github_contributors, dict):
            # it's an error resp from the API, doh.
            return None

        if self.github_contributors is None:
            return None

        total_contributions_count = sum([c['contributions'] for c in self.github_contributors])
        for github_contrib in self.github_contributors:
            person = get_or_make_person(github_login=github_contrib["login"])
            percent_total_contribs = round(
                github_contrib["contributions"] / float(total_contributions_count) * 100,
                3
            )
            self._save_contribution(
                person,
                "github_contributor",
                quantity=github_contrib["contributions"],
                percent=percent_total_contribs
            )

    def save_github_owner_to_db(self):
        if not self.github_owner:
            return False

        person = get_or_make_person(github_login=self.github_owner)
        self._save_contribution(person,  "github_owner")


    def _save_contribution(self, person, role, quantity=None, percent=None):
        extant_contrib = self.get_contribution(person.id, role)
        if extant_contrib is None:

            # make the new contrib.
            # there's got to be a better way to make this args thing...
            kwargs_dict = {
                "role": role
            }
            if quantity is not None:
                kwargs_dict["quantity"] = quantity
            if percent is not None:
                kwargs_dict["percent"] = percent

            new_contrib = Contribution(**kwargs_dict)

            # set the contrib in its various places.
            self.contributions.append(new_contrib)
            person.contributions.append(new_contrib)
            db.session.merge(person)


    def get_contribution(self, person_id, role):
        for contrib in self.contributions:
            if contrib.person.id == person_id and contrib.role == role:
                return contrib

        return None

    def set_github_contributors(self):
        self.github_contributors = github_api.get_repo_contributors(
            self.github_owner,
            self.github_repo_name
        )
        print "found github contributors", self.github_contributors

    def set_github_repo_id(self):
        # override in subclass
        raise NotImplementedError


    @property
    def contributors(self):
        ret = []
        for contrib in self.contributions:
            ret.append(contrib.person)

        return ret




class PypiPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'pypi'
    }

    def __repr__(self):
        return u'<PypiPackage {name}>'.format(
            name=self.full_name)

    def save_host_contributors(self):
        author = self.api_raw["info"]["author"]
        author_email = self.api_raw["info"]["author_email"]

        if not author:
            return False

        if author_email and validate_email(author_email):
            person = get_or_make_person(name=author, email=author_email)
        else:
            person = get_or_make_person(name=author)

        self._save_contribution(person, "author")


    def set_github_repo_ids(self):
        q = db.session.query(GithubRepo.login, GithubRepo.repo_name)
        q = q.filter(GithubRepo.bucket.contains({"setup_py_name": self.project_name}))
        q = q.order_by(GithubRepo.api_raw['stargazers_count'].cast(db.Integer).desc())

        start = time()
        row = q.first()
        print "Github repo query took {}".format(elapsed(start, 4))
        start = time()
        db.session.expunge_all()
        db.session.remove()
        print "Github repo expunge and remove took {}".format(elapsed(start, 4))

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



class CranPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'cran'
    }

    def __repr__(self):
        return u'<CranPackage {name}>'.format(
            name=self.full_name)

    def save_host_contributors(self):
        all_authors = self.api_raw["Author"]
        maintainer = self.api_raw["Maintainer"]




        #if not author:
        #    return False
        #
        #if author_email and validate_email(author_email):
        #    person = get_or_make_person(name=author, email=author_email)
        #else:
        #    person = get_or_make_person(name=author)
        #
        #self._save_contribution(person, "author")



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





def save_host_contributors_pypi(limit=10):
    # has to be run all in one go, db stores no indicator this has run.
    q = db.session.query(PypiPackage.full_name)
    q = q.order_by(Package.project_name)
    q = q.limit(limit)

    update_fn = make_update_fn(Package, "save_host_contributors")
    for row in q.all():
        update_fn(row[0])

def save_host_contributors_cran(limit=10):
    # has to be run all in one go, db stores no indicator this has run.
    q = db.session.query(CranPackage.full_name)
    q = q.order_by(Package.project_name)
    q = q.limit(limit)

    update_fn = make_update_fn(Package, "save_host_contributors")
    for row in q.all():
        update_fn(row[0])





def set_all_github_contributors(limit=10, use_rq="rq"):
    q = db.session.query(Package.full_name)
    q = q.filter(Package.github_repo_name != None)
    q = q.filter(Package.github_contributors == None)
    q = q.order_by(Package.project_name)
    q = q.limit(limit)

    enqueue_jobs(Package, "set_github_contributors", q, 1, use_rq)




# this is the one that works, make them like this from now on
def test_package(limit=10, use_rq="rq"):

    q = db.session.query(Package.full_name)
    q = q.filter(Package.github_owner != None)
    q = q.order_by(Package.project_name)
    q = q.limit(limit)

    enqueue_jobs(Package, "test", q, 1, use_rq)






def set_all_pypi_github_repo_ids(limit=10, use_rq="rq"):

    q = db.session.query(PypiPackage.full_name)
    q = q.filter(PypiPackage.github_repo_name == None)
    q = q.order_by(PypiPackage.project_name)
    q = q.limit(limit)

    enqueue_jobs(Package, "set_github_repo_ids", q, 1, use_rq)





def set_all_cran_github_repo_ids(limit=10, use_rq="rq"):

    q = db.session.query(CranPackage.full_name)
    q = q.filter(CranPackage.github_repo_name == None)
    q = q.order_by(CranPackage.project_name)
    q = q.limit(limit)

    enqueue_jobs(CranPackage, "set_github_repo_ids", q, 1, use_rq)





def make_persons_from_github_owner_and_contribs(limit=10, use_rq="rq"):
    q = db.session.query(Package.full_name)
    q = q.filter(Package.github_repo_name != None)
    q = q.filter(Package.bucket.contains({"matched_from_github_metadata": True}))
    q = q.order_by(Package.full_name)
    q = q.limit(limit)

    enqueue_jobs(Package, "save_github_owners_and_contributors", q, 1, use_rq)










