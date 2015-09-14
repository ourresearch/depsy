from app import db
from sqlalchemy.dialects.postgresql import JSONB

from util import dict_from_dir

# sqla needs these two imports when you get started:
#from models import package
#from models import person

class Contribution(db.Model):
    __tablename__ = 'contribution'

    id = db.Column(db.Integer, primary_key=True)

    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    package_id = db.Column(db.Text, db.ForeignKey("package.id"))

    #person = db.relationship("Person", backref="contributions")
    #package = db.relationship("Package", backref="contributions")

    role = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    percent = db.Column(db.Float)

    def __repr__(self):
        return u"Contribution from Person #{} to Package {}".format(
            self.person_id,
            self.package_id
        )

    def to_dict(self):
        ret = {
            "role": self.role,
            "quantity": self.quantity,
            "percent": self.percent,
            "package": self.package.to_dict(full=False),
            "person": self.person.to_dict(full=False)
        }
        return ret





