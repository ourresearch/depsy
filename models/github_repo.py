from app import db
from sqlalchemy.dialects.postgresql import JSON


class GithubRepo(db):
    login = db.Column(db.Text, primary_key=True)
    repo_name = db.Column(db.Text, primary_key=True)
    api_raw = db.Column(JSON)






def add_python_repos_from_google_bucket():
    url = "https://storage.googleapis.com/impactstory/github_python_repo_names.csv"
    add_repos_from_remote_csv(url)


def add_repos_from_remote_csv(csv_url):
    pass