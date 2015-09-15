from models.person import Person
from models.package import PypiPackage
from models.package import CranPackage
from models.package import Package
from models.tag import Tag

from app import db

def autocomplete(search_str):

    ret = []


    # pypi packages
    q = db.session.query(PypiPackage)
    q = q.filter(PypiPackage.project_name.ilike("%{}%".format(search_str)))
    q = q.order_by(PypiPackage.sort_score.desc())
    q = q.limit(5)

    first = True
    print "got Packages", q.all()
    for package in q.all():
        d = package.as_search_result
        d["first"] = first
        ret.append(d)
        first = False


    # cran packages
    q = db.session.query(CranPackage)
    q = q.filter(CranPackage.project_name.ilike("%{}%".format(search_str)))
    q = q.order_by(CranPackage.sort_score.desc())
    q = q.limit(5)

    first = True
    print "got Packages", q.all()
    for package in q.all():
        d = package.as_search_result
        d["first"] = first
        ret.append(d)
        first = False


    # persons
    q = db.session.query(Person)
    q = q.filter(Person.name.ilike("%{}%".format(search_str)))
    q = q.order_by(Person.sort_score.desc())
    q = q.limit(5)

    first = True
    print "got Persons", q.all()
    for person in q.all():
        d = person.as_search_result
        d["first"] = first
        ret.append(d)
        first = False

    # tags
    q = db.session.query(Tag)
    q = q.filter(Tag.name.ilike("%{}%".format(search_str)))
    q = q.order_by(Tag.count.desc())
    q = q.limit(5)

    first = True
    print "got tags", q.all()
    for tag in q.all():
        d = tag.as_search_result
        d["first"] = first
        ret.append(d)
        first = False


    return ret










