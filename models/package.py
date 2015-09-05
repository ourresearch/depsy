from app import db
from sqlalchemy.dialects.postgresql import JSONB
from util import elapsed
from time import time


from models import github_api
from models.person import Person
from models.person import get_or_make_person
from models.contribution import Contribution

class Package(db.Model):
    full_name = db.Column(db.Text, primary_key=True)
    host = db.Column(db.Text)
    project_name = db.Column(db.Text)

    github_owner = db.Column(db.Text)
    github_repo_name = db.Column(db.Text)

    api_raw = db.Column(JSONB)
    downloads = db.Column(JSONB)

    github_reverse_deps = db.Column(JSONB)
    host_reverse_deps = db.Column(JSONB)
    dependencies = db.Column(JSONB)

    proxy_papers = db.Column(db.Text)
    github_contributors = db.Column(JSONB)

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
        q = db.session.query(cls.project_name).filter(cls.project_name.in_(module_names))
        response = [row[0] for row in q.all()]
        return response


    def save_contributors_to_db(self):

        if isinstance(self.github_contributors, dict):
            # it's an error resp from the API, doh.
            return None

        for github_contrib in self.github_contributors:
            person = get_or_make_person(github_login=github_contrib["login"])

            extant_contrib = self.get_contribution(person.id, "github_contributor")
            if extant_contrib is None:
                new_contrib = Contribution(
                    role="github_contributor",
                    quantity=github_contrib["contributions"]
                )
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
        print self.github_contributors

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



class CranPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'cran'
    }

    def __repr__(self):
        return u'<CranPackage {name}>'.format(
            name=self.full_name)




def test_package():

    my_package = db.session.query(Package).get('pypi:2mp4')

    print my_package.save_contributors_to_db()

    #my_package.save_contributors_to_db()
    #db.session.commit()


    #contrib = Contribution(role="author")
    #my_person = Person(name="jason1 test", email="test1@foo.com")
    #my_person.contributions.append(contrib)
    #my_package.contributions.append(contrib)
    #db.session.add(my_person)
    #db.session.merge(my_package)

def make_persons_from_github_contribs(limit=10):
    q = db.session.query(Package.full_name)
    q = q.filter(Package.github_contributors != None)
    q = q.order_by(Package.project_name)
    q = q.limit(limit)

    update_fn = make_update_fn("save_contributors_to_db")

    for row in q.all():
        update_fn(row[0])




"""
get github contrib info.

here as an example we were using it in the old cran_project module.
"""
def set_all_github_contributors(limit=10):
    q = db.session.query(Package.full_name)
    q = q.filter(Package.github_repo_name != None)
    q = q.order_by(Package.project_name)
    q = q.limit(limit)

    update_fn = make_update_fn("set_github_contributors")

    for row in q.all():
        update_fn(row[0])






def make_update_fn(method_name):
    def fn(obj_id):
        start_time = time()

        obj = db.session.query(Package).get(obj_id)
        if obj is None:
            return None

        method_to_run = getattr(obj, method_name)

        print "running {repr}.{method_name}() method".format(
            repr=obj,
            method_name=method_name
        )

        method_to_run()
        db.session.commit()

        print "finished {repr}.{method_name}(). took {elapsted}sec".format(
            repr=obj,
            method_name=method_name,
            elapsted=elapsed(start_time, 4)
        )
        return None  # important for if we use this on RQ

    return fn