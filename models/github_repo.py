from app import db
from sqlalchemy.dialects.postgresql import JSONB

from models.github_api import username_and_repo_name_from_github_url
from models import github_api
import requests
from util import elapsed
from time import time

class GithubRepo(db.Model):
    login = db.Column(db.Text, primary_key=True)
    repo_name = db.Column(db.Text, primary_key=True)
    language = db.Column(db.Text)
    api_raw = db.Column(JSONB)
    dependency_lines = db.Column(db.Text)

    def __repr__(self):
        return u'<GithubRepo {language} {login}/{repo_name}>'.format(
            language=self.language, login=self.login, repo_name=self.repo_name)

    def set_github_about(self):
        self.api_raw = github_api.get_repo_data(self.login, self.repo_name)

    def set_github_dependency_lines(self):
        self.dependency_lines = github_api.get_repo_dependency_lines(
            self.login, 
            self.repo_name, 
            self.language
            )


# call python main.py add_python_repos_from_google_bucket to run
def add_python_repos_from_google_bucket():

    url = "https://storage.googleapis.com/impactstory/github_python_repo_names.csv"
    add_repos_from_remote_csv(url, "python")


# call python main.py add_r_repos_from_google_bucket to run
def add_r_repos_from_google_bucket():

    url = "https://storage.googleapis.com/impactstory/github_r_repo_names.csv"
    add_repos_from_remote_csv(url, "r")



def add_repos_from_remote_csv(csv_url, language):
    start = time()

    print "going to go get file"
    response = requests.get(csv_url, stream=True)
    index = 0

    for github_url in response.iter_lines(chunk_size=1000):
        login, repo_name = username_and_repo_name_from_github_url(github_url)
        if login and repo_name:
            repo = GithubRepo(
                login=login,
                repo_name=repo_name, 
                language=language
            )
            print repo
            db.session.merge(repo)
            index += 1
            if index % 1000 == 0:
                db.session.commit()
                print "flushing on index {index}, elapsed: {elapsed}".format(
                    index=index, 
                    elapsed=elapsed(start))

    db.session.commit()


def add_all_github_about():
    q = db.session.query(GithubRepo.login, GithubRepo.repo_name)
    q = q.filter(GithubRepo.api_raw == 'null')
    q = q.order_by(GithubRepo.login)

    for row in q.all():
        #print "setting this row", row
        add_github_about(row[0], row[1])

def add_github_about(login, repo_name):
    repo = db.session.query(GithubRepo).get((login, repo_name))
    repo.set_github_about()
    db.session.commit()

    print repo


def add_github_dependency_lines(login, repo_name):
    repo = db.session.query(GithubRepo).get((login, repo_name))
    repo.set_github_dependency_lines()
    db.session.commit()

    print repo

