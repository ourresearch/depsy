from app import db
from sqlalchemy.dialects.postgresql import JSONB
from models.package import make_language



class Tags(db.Model):
    id = db.Column(db.Text, primary_key=True)
    unique_tag = db.Column(db.Text)
    namespace = db.Column(db.Text)
    count = db.Column(db.Integer)

    def __repr__(self):
        return u'<Tag "{}">'.format(self.id)

    @property
    def as_snippet(self):

        ret = {
        	"language": make_language(self.namespace),
        	"count": self.count,
        	"name": self.unique_tag,
        }

        return ret