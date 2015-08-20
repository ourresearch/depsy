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
    github_repo = get_github_homepage(pypi_dict["info"]["home_page"])

    return PyPiRepo(
        name=name,
        github_repo=github_repo,
        raw_json=json.dumps(pypi_dict, indent=3, sort_keys=True)
    )



class PyPiRepo(db.Model):
    __tablename__ = 'pypi_repo'
    name = db.Column(db.Text, primary_key=True)
    github_repo = db.Column(db.Text)
    raw_json = db.Column(db.Text)

    #collected = db.Column(db.DateTime())
    #downloads_last_month = db.Column(db.Integer)
    #downloads_ever = db.Column(db.Integer)
    #requires = db.Column(JSON)