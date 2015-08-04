from app import db
from sqlalchemy.dialects.postgresql import JSON
import datetime
import shortuuid
import logging

from util import dict_from_dir
from util import underscore_to_camelcase

logger = logging.getLogger("snap")



class Snap(db.Model):
    snap_id = db.Column(db.Text, primary_key=True)    
    repo_id = db.Column(db.Text, db.ForeignKey("repo.repo_id", onupdate="CASCADE", ondelete="CASCADE"))    
    provider = db.Column(db.Text)
    data = db.Column(JSON)
    collected = db.Column(db.DateTime())

    def __init__(self, **kwargs):
        print "creating a snap with these keyword args", kwargs

        if not "snap_id" in kwargs:
            self.snap_id = shortuuid.uuid()                 
        self.collected = datetime.datetime.utcnow().isoformat()
        super(Snap, self).__init__(**kwargs)

    def __repr__(self):
        return u'<Snap {snap_id} {repo_id} {provider}>'.format(
            snap_id=self.snap_id, repo_id=self.repo_id, provider=self.provider)



def make_working_snap(snap):
    """
    Instantiates one of the specific WorkingSnap classes from a generic db Snap
    """
    new_class_name = underscore_to_camelcase(snap.provider) + "Snap"
    new_class = globals()[new_class_name](snap)
    return new_class


class WorkingSnap():
    def __init__(self, snap):
        print "making a new workingsnap!"
        self.snap = snap

    @property
    def provider(self):
        return self.snap.provider

    def to_dict(self):
        keys_to_ignore = ["snap"]
        return dict_from_dir(self, keys_to_ignore)


class GithubSubscribersSnap(WorkingSnap):

    @property
    def subscribers(self):
        return self.snap.data

    @property
    def subscribers_count(self):
        return len(self.snap.data)



class CrantasticDailyDownloadsSnap(WorkingSnap):

    @property
    def subscribers(self):
        return self.snap.data


class CranReverseDependencies(WorkingSnap):

    @property
    def subscribers(self):
        return self.snap.data









