from app import db
from sqlalchemy.dialects.postgresql import JSON
from models.github_api import make_call

class GithubUser(db.Model):
    login = db.Column(db.Text, primary_key=True)
    is_404 = db.Column(db.Boolean)

    github_about = db.deferred(db.Column(JSON))





