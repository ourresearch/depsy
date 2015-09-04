from app import db
from sqlalchemy.dialects.postgresql import JSONB

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

    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'person',
        'with_polymorphic': '*'
    }
    def print_favorite_word(self):
        print "i'm not sure?"

    def person_thing(self):
        print "i am a person, that i am"


class GithubPerson(Person):
    __mapper_args__ = {
        'polymorphic_identity': 'githubperson'
    }



def test_person():
    #p = FooPerson(email="1@fooperson.com")
    #db.session.add(p)
    #db.session.commit()

    res_obj = db.session.query(Person).get(1)
    print "got this:", res_obj.email, res_obj.type
    res_obj.person_thing()

    print "i'm in the person module."