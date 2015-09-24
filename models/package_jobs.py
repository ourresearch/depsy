from app import db
from models.package import Package
from models.pypi_package import PypiPackage
from models.cran_package import CranPackage

def get_packages(sort="sort_score", filters=None):

    q = db.session.query(Package)
    q = q.order_by(Package.pagerank.desc())
    q = q.order_by(Package.num_downloads.desc())

    q = q.limit(25)

    ret = q.all()
    return ret

