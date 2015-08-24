from app import db
from sqlalchemy.dialects.postgresql import JSON

import requests

class GithubRepo(db.Model):
    login = db.Column(db.Text, primary_key=True)
    repo_name = db.Column(db.Text, primary_key=True)
    language = db.Column(db.Text)
    api_raw = db.Column(JSON)






def add_python_repos_from_google_bucket():
    # call python main.py add_python_repos_from_google_bucket to run

    url = "https://storage.googleapis.com/impactstory/github_python_repo_names.csv"
    add_repos_from_remote_csv(url)


def add_repos_from_remote_csv(csv_url):
    print "going to go get file"
    response = requests.get(csv_url)
    contents = response.text
    lines = contents.split("\n")
    for line in lines:




    pass