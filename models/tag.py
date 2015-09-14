from app import db
from sqlalchemy.dialects.postgresql import JSONB

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text)
    name = db.Column(db.Text)
    other_names = db.Column(JSONB)
    github_login = db.Column(db.Text)
    github_about = db.deferred(db.Column(JSONB))
    bucket = db.Column(JSONB)
    sort_score = db.Column(db.Float)

    type = db.Column(db.Text)


    def __repr__(self):
        return u'<Person names "{name}" ({id})>'.format(
            name=self.name,
            id=self.id
        )