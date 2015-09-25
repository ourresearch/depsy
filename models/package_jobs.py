from app import db
from models.package import Package
from models.pypi_package import PypiPackage
from models.cran_package import CranPackage
from jobs import update_registry
from jobs import Update

def get_packages(sort="sort_score", filters=None):

    q = db.session.query(Package)
    q = q.order_by(Package.pagerank.desc())
    q = q.order_by(Package.num_downloads.desc())

    q = q.limit(25)

    ret = q.all()
    return ret



q = db.session.query(CranPackage.id)
update_registry.register(Update(
    job=CranPackage.set_rev_deps_tree,
    query=q,
    shortcut_fn=CranPackage.shortcut_rev_deps_pairs
))

q = db.session.query(PypiPackage.id)
update_registry.register(Update(
    job=PypiPackage.set_rev_deps_tree,
    query=q,
    shortcut_fn=PypiPackage.shortcut_rev_deps_pairs
))
