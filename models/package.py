from app import db
from sqlalchemy.dialects.postgresql import JSONB
from util import elapsed
from time import time

from models import github_api

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


    def set_github_contributors(self):
        self.github_contributors = github_api.get_repo_contributors(
            self.github_owner,
            self.github_repo_name
        )
        print "added github contributors!"
        print self.github_contributors



class PypiPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'pypi'
    }


class CranPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'cran'
    }




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
        method_to_run()

        db.session.commit()

        print "ran {repr}.{method_name}() method  and committed. took {elapsted}sec".format(
            repr=obj,
            method_name=method_name,
            elapsted=elapsed(start_time, 4)
        )
        return None  # important for if we use this on RQ

    return fn