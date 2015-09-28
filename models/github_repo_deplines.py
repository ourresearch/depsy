from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import DataError
from sqlalchemy import or_
from sqlalchemy.orm import deferred

class GithubRepoDeplines(db.Model):
    __bind_key__ = "old_db"
    __tablename__ = "old_github_repo"

    id = db.Column(db.Text)
    login = db.Column(db.Text, primary_key=True)
    repo_name = db.Column(db.Text, primary_key=True)
    dependency_lines = db.Column(db.Text)
    zip_filenames = db.Column(JSONB)

    def say_hi(self):
        print u"hi! from {} {}.".format(self.login, self.repo_name)
        if self.dependency_lines:
            print u"my dep_lines is {} long".format(len(self.dependency_lines))

