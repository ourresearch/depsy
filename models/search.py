from models.person import Person
from models.package import Package
from models.tag import Tag

from app import db

def autocomplete(search_str):

    tags_q = db.session.query(Tag)
    tags_q = tags_q.filter(Tag.name.ilike("%{}%".format(search_str)))
    tags_q = tags_q.order_by(Tag.count.desc())
    tags_q = tags_q.limit(5)

    ret = []
    first = True
    print "got tags", tags_q.all()
    for tag in tags_q.all():
        ret.append({
            "type": "tag",
            "name": tag.name,
            "count": tag.count,
            "first": first
        })
        first = False

    return ret