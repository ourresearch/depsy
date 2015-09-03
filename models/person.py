from app import db



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



class Person(db):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'person',
        'with_polymorphic': '*'
    }


class GithubPerson(Person):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity':'person',
        'with_polymorphic': '*'
    }


"""