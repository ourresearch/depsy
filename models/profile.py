from app import db
from models.repo import create_repo
from models.repo import Repo
from providers import github
from util import dict_from_dir

from sqlalchemy.dialects.postgresql import JSON
import datetime
import logging

logger = logging.getLogger("profile")


def create_profile(username):
    profile_data = github.get_profile_data(username)
    profile = Profile(username=username, github_data=profile_data)

    repo_data = github.get_all_repo_data(username)
    for repo_dict in repo_data:
        repo = create_repo(username, repo_dict["name"], repo_dict)
        profile.repos.append(repo)
    db.session.merge(profile)
    db.session.commit()
    return profile


class Profile(db.Model):
    username = db.Column(db.Text, primary_key=True)
    created = db.Column(db.DateTime())
    github_data = db.Column(JSON)

    repos = db.relationship(
        'Repo',
        lazy='subquery',
        cascade='all, delete-orphan'

        # @heather
        # i removed this line:
        # backref=db.backref("repo", lazy="subquery")
        # because it seemed to be making circular references on the repo obj
    )

    def __init__(self, **kwargs):
        super(Profile, self).__init__(**kwargs)
        self.created = datetime.datetime.utcnow().isoformat()

    def __repr__(self):
        return u'<Profile {username}>'.format(
            username=self.username)

    def _get_from_github_data(self, my_property):
        try:
            return self.github_data[my_property]
        except KeyError:
            return None

    @property
    def avatar_url(self):
        return self._get_from_github_data("avatar_url")

    @property
    def bio(self):
        return self._get_from_github_data("bio")

    @property
    def blog(self):
        return self._get_from_github_data("blog")

    @property
    def company(self):
        return self._get_from_github_data("company")

    @property
    def created_at(self):
        return self._get_from_github_data("created_at")

    @property
    def email(self):
        return self._get_from_github_data("email")

    @property
    def followers(self):
        return self._get_from_github_data("followers")

    @property
    def following(self):
        return self._get_from_github_data("following")

    @property
    def html_url(self):
        return self._get_from_github_data("html_url")

    @property
    def location(self):
        return self._get_from_github_data("location")

    @property
    def received_events_url(self):
        return self._get_from_github_data("received_events_url")

    @property
    def updated_at(self):
        return self._get_from_github_data("updated_at")

    def to_dict(self):
        return dict_from_dir(self, keys_to_ignore=["github_data"])
