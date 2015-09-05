from app import db
from sqlalchemy.dialects.postgresql import JSONB
from github_api import get_profile

"""
this file in progress. i think should have:

Person table
id
email
name
other names jsonb
has_github bool
github login
github about
"""


class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text)
    name = db.Column(db.Text)
    other_names = db.Column(JSONB)
    github_login = db.Column(db.Text)
    github_about = db.Column(JSONB)

    type = db.Column(db.Text)
    contributions = db.relationship(
        'Contribution',
        lazy='subquery',
        cascade="all, delete-orphan",
        backref=db.backref("person", lazy="subquery")
    )

    def __repr__(self):
        return u'<Person {id}: {name}>'.format(
            id=self.id,
            name=self.name
        )

    def set_github_about(self):
        if self.github_login is not None:
            self.github_about = get_profile(self.github_login)




def get_or_make_person(**kwargs):
    res = None
    if "github_login" in kwargs:
        res = db.session.query(Person).filter(
            Person.github_login == kwargs["github_login"]
        ).first()

    elif "email" in kwargs:
        res = db.session.query(Person).filter(
            Person.email == kwargs["email"]
        ).first()

    if res is not None:
        return res
    else:
        new_person = Person(**kwargs)
        db.session.add(new_person)
        db.session.commit()

        return new_person







def test_person():

    res_obj = db.session.query(Person).get(1)
    print "got this:", res_obj.email, res_obj.type

    print "i'm in the person module."