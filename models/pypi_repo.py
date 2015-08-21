from app import db

from urlparse import urlparse
import json



def get_github_homepage(url):
    try:
        parsed = urlparse(url)
    except AttributeError:
        return None  # no url was given

    # we are getting rid of things that
    # 1. aren't on github (duh)
    # 2. are just "github.com"
    # this leaves some things that have multiple pypi project in one github repo
    if parsed.netloc == "github.com" and len(parsed.path.split("/")) > 1:
        return url
    else:
        return None


def make_pypi_repo(pypi_dict):
    name = pypi_dict["info"]["name"]
    github_url = get_github_homepage(pypi_dict["info"]["home_page"])

    # i'm pretty sure this will break when you give it None, fix later.
    path = urlparse(github_url).path

    return PyPiRepo(
        pypi_name=name,
        github_repo_owner=path[1],
        github_repo_name=path[2],
        github_url=github_url,
        pypi_json=json.dumps(pypi_dict, indent=3, sort_keys=True)
    )



class PyPiRepo(db.Model):
    __tablename__ = 'pypi_repo'
    pypi_name = db.Column(db.Text, primary_key=True)
    github_url = db.Column(db.Text)
    github_repo_name = db.Column(db.Text)
    github_repo_owner = db.Column(db.Text)
    pypi_json = db.deferred(db.Column(db.Text))

    #collected = db.Column(db.DateTime())
    #downloads_last_month = db.Column(db.Integer)
    #downloads_ever = db.Column(db.Integer)
    #requires = db.Column(JSON)

    @property
    def name_tuple(self):
        return (self.github_repo_owner, self.github_repo_name)