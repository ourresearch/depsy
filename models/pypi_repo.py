from __future__ import division
from app import db
from models.github_api import make_ratelimited_call
from models.github_api import GithubRateLimitException
from models.github_user import GithubUser
from util import elapsed
from urlparse import urlparse
import json
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import OperationalError
from time import time



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
    # this is out of date and no longer will work...
    name = pypi_dict["info"]["name"]
    github_url = get_github_homepage(pypi_dict["info"]["home_page"])

    # i'm pretty sure this will break when you give it None, fix later.
    path = urlparse(github_url).path

    return PyPiRepo(
        pypi_name=name,
        repo_owner=path[1],
        repo_name=path[2],
        github_url=github_url,
        pypi_about=json.dumps(pypi_dict, indent=3, sort_keys=True)
    )





class PyPiRepo(db.Model):
    __tablename__ = 'pypi_repo'
    pypi_name = db.Column(db.Text, primary_key=True)
    github_url = db.Column(db.Text)
    repo_name = db.Column(db.Text)
    repo_owner = db.Column(db.Text)

    commit_counts = db.Column(JSON)
    commit_percents = db.Column(JSON)
    key_committers = db.Column(JSON)

    is_404 = db.Column(db.Boolean)
    pypi_about = db.deferred(db.Column(db.Text))
    github_about = db.deferred(db.Column(JSON))

    #collected = db.Column(db.DateTime())
    #downloads_last_month = db.Column(db.Integer)
    #downloads_ever = db.Column(db.Integer)
    #requires = db.Column(JSON)

    @property
    def name_tuple(self):
        return (self.repo_owner, self.repo_name)

    def set_repo_commits(self):
        url = "https://api.github.com/repos/{username}/{repo_name}/contributors".format(
            username=self.repo_owner,
            repo_name=self.repo_name
        )
        resp = make_ratelimited_call(url)
        if resp is None:
            self.is_404 = True
            return False

        # set the commit_lines property
        self.commit_counts = {}
        for contrib_dict in resp:
            contrib_login = contrib_dict["login"]
            self.commit_counts[contrib_login] = contrib_dict["contributions"]

        # set the commit_percents property
        total_commits = sum(self.commit_counts.values())
        self.commit_percents = {}
        for username, count in self.commit_counts.iteritems():
            self.commit_percents[username] = int(round(count / total_commits * 100))

        # set the key_committer property
        # do later.
        self.key_committers = {}
        for username, count in self.commit_counts.iteritems():
            percent = self.commit_percents[username]
            if percent >= 25 or count >= 100:
                self.key_committers[username] = True
            else:
                self.key_committers[username] = False

        return True


def save_all_repo_owners_and_key_committers():
    start = time()
    q = db.session.query(PyPiRepo.repo_owner)\
        .filter(PyPiRepo.repo_owner.isnot(None))\
        .filter(PyPiRepo.is_404.isnot(True))

    logins = set()
    for res in q.all():
        logins.add(res[0])

    print "got {} logins from repo owners".format(len(logins))

    q2 = db.session.query(PyPiRepo.key_committers)\
        .filter(PyPiRepo.key_committers.isnot(None))\
        .filter(PyPiRepo.is_404.isnot(True))

    for res in q2.all():
        for login, is_key in res[0].iteritems():
            if is_key:
                logins.add(login)

    print "got {} logins including key committers".format(len(logins))

    index = 0
    for login in logins:
        user = GithubUser(login=login)
        db.session.add(user)
        print "{}: {}".format(index, login)
        index += 1
        if index % 100 == 0:
            print "flushing to db...\n\n"
            db.session.flush()

    db.session.commit()
    return True



def set_all_repo_commits():
    start = time()
    index = 0
    q = db.session.query(PyPiRepo)\
        .filter(PyPiRepo.repo_name.isnot(None))\
        .filter(PyPiRepo.repo_owner.isnot(None))\
        .filter(PyPiRepo.is_404.isnot(True))\
        .filter(PyPiRepo.commit_counts.is_(None))\
        .limit(5000)

    for repo in q.yield_per(100):
        try:
            repo.set_repo_commits()
            index += 1

            print "#{index} ({sec}sec): ran set_repo_commits() for {owner}/{name}".format(
                index=index,
                sec=elapsed(start),
                owner=repo.repo_owner,
                name=repo.repo_name
            )

        except GithubRateLimitException:
            print "ran out of api keys. committing...\n\n".format(
                num=index,
                sec=elapsed(start)
            )
            db.session.commit()
            return False

        if index % 100 == 0:
            try:
                db.session.flush()
            except OperationalError:
                print "problem with flushing the session. rolling back."
                db.session.rollback()
                continue



    print "finished updating repos! committing...".format(
        num=index,
        sec=elapsed(start)
    )
    db.session.commit()
    return True













