from app import db
from sqlalchemy.dialects.postgresql import JSON

# define the briding table,
# from http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html#building-a-many-to-many-relationship
repo2_user = db.Table('repo2_user', db.metadata,
    db.Column('repo2_name', db.Text, db.ForeignKey('repo2.repo2_name')),
    db.Column('github_user_login', db.Text, db.ForeignKey('github_user.login'))
    )





class Repo2(db.Model):

    # eg: "jasonpriem/php-name-parse"
    repo2_name = db.Column(db.Text, primary_key=True)

    github_about = db.Column(JSON)
    github_stats = db.Column(JSON)
    collected = db.Column(db.DateTime())

    github_users = db.relationship(
        'Keyword',
        secondary=post_keywords,
        backref='posts'
    )

    snaps = db.relationship(
        'Snap',
        lazy='subquery',
        cascade='all, delete-orphan'
    )



class GithubUser(db.Model):
    login = db.Column(db.Text, primary_key=True)
    github_data = db.Column(JSON)
    collected = db.Column(db.DateTime())

    repos = db.relationship(
        'Repo',
        lazy='subquery',
        cascade='all, delete-orphan'

        # @heather
        # i removed this line:
        # backref=db.backref("repo", lazy="subquery")
        # because it seemed to be making circular references on the repo obj
    )