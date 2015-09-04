from app import db
from sqlalchemy.dialects.postgresql import JSONB


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
        'polymorphic_identity': 'package',
        'with_polymorphic': '*'
    }

    def __repr__(self):
        return u'<Package {name}>'.format(
            name=self.full_name)


class PypiPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'pypi'
    }


class CranPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'cran'
    }




def test_package():
    res_obj = db.session.query(Package).get('pypi:11')

    print "testing package.py!", res_obj