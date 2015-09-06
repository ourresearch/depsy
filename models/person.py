from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import text

from github_api import get_profile
from jobs import make_update_fn
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
        return u'<Person names "{name}" ({id})>'.format(
            name=self.name,
            id=self.id
        )

    def set_github_about(self):
        if self.github_login is None:
            return None

        self.github_about = get_profile(self.github_login)
        try:
            if not self.name:
                self.name = self.github_about["name"]

            if not self.email :
                self.email = self.github_about["email"]
        except KeyError:

            # our github_about is an error object,
            # it's got no info about the person in it.
            return False



def get_github_about_for_all_persons(limit=10):
    q = db.session.query(Person.id)
    q = q.filter(Person.github_about == text("'null'"))  # jsonb null, not sql NULL
    q = q.order_by(Person.id)
    q = q.limit(limit)

    update_fn = make_update_fn(Person, "set_github_about")

    for row in q.all():
        update_fn(row[0])



def get_or_make_person(**kwargs):
    res = None


    if kwargs["name"] == "UNKNOWN":
        # pypi sets unknown people to have the name "UNKNOWN"
        # we don't want to make tons of these, it's just one 'person'.
        res = db.session.query(Person).filter(
            Person.name == "UNKNOWN"
        ).first()

    if kwargs["name"] == "ORPHANED":
        # cran sets this when the maintainer is gone.
        # we don't want to make tons of these, it's just one 'person'.
        res = db.session.query(Person).filter(
            Person.name == "ORPHANED"
        ).first()

    if res is not None:
        return res



    if "github_login" in kwargs:
        res = db.session.query(Person).filter(
            Person.github_login == kwargs["github_login"]
        ).first()

    elif "email" in kwargs:
        res = db.session.query(Person).filter(
            Person.email == kwargs["email"]
        ).first()
        if res is not None:
            print u"we matched a person ({}) based on email {}".format(
                res,
                kwargs["email"]
            )

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