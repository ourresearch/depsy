from app import db
from models.snap import Snap
from models.snap import make_working_snap
from providers import github_subscribers
from providers import crantastic_daily_downloads
from providers import github

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm.collections import attribute_mapped_collection

import importlib
import shortuuid
import datetime
import logging

from util import dict_from_dir

logger = logging.getLogger("repo")

def create_repo(username, reponame, github_data=None):
    if not github_data:
        github_data = github.get_repo_data(username, reponame)
    repo = Repo(username=username, reponame=reponame, github_data=github_data)
    repo.collect_metrics()
    return repo

def get_provider_module(provider_name):
    provider_module = importlib.import_module('providers.'+provider_name)
    return provider_module

def get_provider_class(provider_name):
    provider_module = get_provider_module(provider_name)
    provider = getattr(provider_module, provider_name.title())
    instance = provider()
    return instance


class Repo(db.Model):
    repo_id = db.Column(db.Text, primary_key=True)
    username = db.Column(db.Text, db.ForeignKey("profile.username", onupdate="CASCADE", ondelete="CASCADE"))
    reponame = db.Column(db.Text)
    github_data = db.Column(JSON)
    collected = db.Column(db.DateTime())
    snaps = db.relationship(
        'Snap',
        lazy='subquery',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):   
        if not "repo_id" in kwargs:
            self.repo_id = shortuuid.uuid()

        # @heather
        # does "collected" mean "created" here? -j
        self.collected = datetime.datetime.utcnow().isoformat()
        super(Repo, self).__init__(**kwargs)

    @property
    def language(self):
        return self.github_data.get("language", None)

    @property
    def github_forks_count(self):
        return self.github_data["forks_count"]

    @property
    def github_stargazers_count(self):
        return self.github_data["stargazers_count"]

    @property
    def computed_snaps(self):
        ret = []
        for snap in self.snaps:
            ret.append(make_working_snap(snap))

        return ret



    def collect_metrics(self):
        data = github_subscribers.get_data(self.username, self.reponame)
        if data:
            #self.snaps["github_subscribers"] = Snap(provider="github_subscribers", data=data)
            self.snaps.append(Snap(provider="github_subscribers", data=data))

        #if self.language == "R":
        #    r_providers = [
        #        "crantastic_daily_downloads",
        #        "cran_reverse_dependencies"
        #    ]
        #    for provider_name in r_providers:
        #        provider = get_provider_module(provider_name)
        #        data = provider.get_data(self.reponame)
        #        if data:
        #            self.snaps[provider_name] = Snap(provider=provider_name, data=data)


    def _get_from_github_data(self, my_property):
        try:
            return self.github_data[my_property]
        except KeyError:
            return None


    def created_at(self):
        return self._get_from_github_data("created_at")

    def description(self):
        return self._get_from_github_data("description")

    def language(self):
        return self._get_from_github_data("language")

    def name(self):
        return self._get_from_github_data("name")


    def to_dict(self, keys_to_show="all"):
        keys_to_ignore = [
            # getting these in self.computed_snaps
            "snaps",

            # no need for the raw data, it's unwieldy
            "github_data"
        ]
        ret = dict_from_dir(self, keys_to_ignore)
        return ret

    def __repr__(self):
        return u'<Repo {username}/{reponame}>'.format(
            username=self.username, reponame=self.reponame)
