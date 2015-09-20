from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import text
from models.contribution import Contribution
from jobs import update_registry
from jobs import Update

from github_api import get_profile
from util import dict_from_dir
import hashlib
from nameparser import HumanName
from collections import defaultdict


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
    github_about = db.deferred(db.Column(JSONB))
    bucket = db.Column(JSONB)
    sort_score = db.Column(db.Float)
    parsed_name = db.Column(JSONB)

    type = db.Column(db.Text)


    def __repr__(self):
        return u'<Person names "{name}" ({id})>'.format(
            name=self.name,
            id=self.id
        )

    contributions = db.relationship(
        'Contribution',
        lazy='select',
        cascade="all, delete-orphan",
        backref="person"
    )


    def to_dict(self, full=True):
        ret = {
            "id": self.id, 
            "name": self.name, 
            "github_login": self.github_login, 
            "sort_score": self.sort_score, 
            "icon": self.icon, 
            "icon_small": self.icon_small, 
            "is_academic": self.is_academic, 
            "id": self.id
        }
        if full:
            ret["person_packages"] = [p.to_dict() for p in self.person_packages]
        return ret




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


    def set_sort_score(self):
        self.sort_score = 0
        for contrib in self.contributions:
            self.sort_score += contrib.fractional_sort_score

        return self.sort_score

    def set_parsed_name(self):
        if not self.name:
            self.parsed_name = None
            return

        name = HumanName(self.name)
        self.parsed_name = name.as_dict()

    @property
    def is_academic(self):
        try:
            return self.bucket["is_academic"]
        except KeyError:
            return False

    def _make_gravatar_url(self, size):
        if self.email is not None:
            hash = hashlib.md5(self.email).hexdigest()
        else:
            hash = hashlib.md5("placeholder@example.com").hexdigest()

        url = "http://www.gravatar.com/avatar/{hash}.jpg?s={size}&d=mm".format(
            hash=hash,
            size=size
        )
        return url

    @property
    def icon(self):
        return self._make_gravatar_url(160)

    @property
    def icon_small(self):
        return self._make_gravatar_url(30)

    @property
    def person_packages(self):
        person_packages = defaultdict(PersonPackage)
        for contrib in self.contributions:
            person_packages[contrib.package.id].set_role(contrib)

        return person_packages.values()



class PersonPackage():
    def __init__(self):
        self.package = None
        self.roles = []

    def set_role(self, contrib):
        if not self.package:
            self.package = contrib.package
        self.roles.append(contrib.role_dict)

    @property
    def credit_points(self):
        ret = 0
        for role in self.roles:
            ret += role["fractional_sort_score"]
        return ret


    def to_dict(self):
        ret = self.package.as_snippet
        ret["roles"] = self.roles
        ret["credit_points"] = self.credit_points
        return ret



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


    if 'name' in kwargs and kwargs["name"] == "UNKNOWN":
        # pypi sets unknown people to have the name "UNKNOWN"
        # we don't want to make tons of these, it's just one 'person'.
        res = db.session.query(Person).filter(
            Person.name == "UNKNOWN"
        ).first()

    if 'name' in kwargs and kwargs["name"] == "ORPHANED":
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

    else:
        pass

    if res is not None:
        return res


    else:
        new_person = Person(**kwargs)
        db.session.add(new_person)

        # we can probably get rid of this commit
        db.session.commit()

        return new_person





# i do not understand why, but this does not work in RQ, you must run in
# a single dyno with --no-rq flag set...takes a good 30min :/
q = db.session.query(Person.id)
q = q.filter(Person.sort_score == None)

update_registry.register(Update(
    job=Person.set_sort_score,
    query=q,
    queue_id=3
))


q = db.session.query(Person.id)
q = q.filter(Person.parsed_name == None)

update_registry.register(Update(
    job=Person.set_parsed_name,
    query=q,
    queue_id=8
))


