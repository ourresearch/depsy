from app import db
from models.snap import Snap
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

    #snaps = db.relationship(
    #    'Snap',
    #    lazy='subquery',
    #    cascade='all, delete-orphan',
    #    collection_class=attribute_mapped_collection('provider'),
    #    backref=db.backref("snap", lazy="subquery")
    #)

    #snaps = db.relationship(
    #    'Snap',
    #    lazy='subquery',
    #    cascade='all, delete-orphan',
    #    backref=db.backref("repo", lazy="subquery")
    #)

    def __init__(self, **kwargs):   
        if not "repo_id" in kwargs:
            self.repo_id = shortuuid.uuid()

        # i think that "collected" is really "created" here? -j
        self.collected = datetime.datetime.utcnow().isoformat()
        super(Repo, self).__init__(**kwargs)

    @property
    def language(self):
        return self.github_data.get("language", None)

    @property
    def github_metrics(self):
        keys_to_return = [
            "forks_count",
            "stargazers_count"
            ]
        smaller_dict = dict([(k, self.github_data[k]) for k in keys_to_return if k in self.github_data])
        return smaller_dict

    @property
    def computed_snaps(self):
        return []

    @property
    def metrics(self):

        # the github metrics are part of this Repo obj, no snaps needed
        metrics_dict = self.github_metrics

        #if 'github_subscribers' in self.snaps:
        #    metrics_dict["subscribers_count"] = len(self.snaps["github_subscribers"].data)
        #    metrics_dict["subscribers"] = self.snaps["github_subscribers"].data
        #
        #if 'crantastic_daily_downloads' in self.snaps:
        #    metrics_dict.update(self.snaps["crantastic_daily_downloads"].data)
        #if 'cran_reverse_dependencies' in self.snaps:
        #    metrics_dict.update(self.snaps["cran_reverse_dependencies"].data)

        return metrics_dict

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
        print "\n\n\n in repo, calling repo.to_dict()\n"
        keys_to_ignore = [
            "snaps",
            "github_data",

            # @heather:
            # i super do not understand this. seem sqlalchemy is putting
            # a "repo" property on this object, which has as its contents
            # the owning Profile object in its entirety. which is circular,
            # and throws all kinds of circularity errors when you try to
            # get this as a dict. no idea how to get rid of it. this is
            # just a band-aid, just be actualy fixed i think. -j
            "repo"
        ]
        ret = dict_from_dir(self, keys_to_ignore)
        return ret

    def __repr__(self):
        return u'<Repo {username}/{reponame}>'.format(
            username=self.username, reponame=self.reponame)
