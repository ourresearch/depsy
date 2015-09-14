from app import db
from sqlalchemy.dialects.postgresql import JSONB

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.text, primary_key=True)
    tag = db.Column(db.Text)
    namespace = db.Column(db.Text)
    count = db.Column(db.Integer)



    def __repr__(self):
        return u'<Tag "{}">'.format(self.id)
