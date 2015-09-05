from app import db
from sqlalchemy.dialects.postgresql import JSONB

# sqla needs these two imports when you get started:
#from models import package
#from models import person

class Contribution(db.Model):
    __tablename__ = 'contribution'

    id = db.Column(db.Integer, primary_key=True)

    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    package_full_name = db.Column(db.Text, db.ForeignKey("package.full_name"))

    role = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    percent = db.Column(db.Float)

    def __repr__(self):
        return u"Contribution from Person #{} to Package {}".format(
            self.person_id,
            self.package_full_name
        )
