from sqlalchemy import text
from sqlalchemy import orm

from app import db
from models.package import Package
from models.package import shortcut_igraph_data_dict
from models.pypi_package import PypiPackage
from models.pypi_package import shortcut_get_pypi_package_names
from models.cran_package import CranPackage
from models.person import Person
from models.contribution import Contribution
from models.github_repo_deplines import GithubRepoDeplines
from models.github_repo import GithubRepo
from jobs import update_registry
from jobs import Update



def get_packages(filters=None, page_size=25):

    q = Package.query.options(
        orm.subqueryload_all(
            Package.contributions, 
            Contribution.person, 
            Person.contributions
        )
    )
    for (filter_attribute, filter_value) in filters:

        if filter_attribute=="language":
            filter_attribute = "host"
            if filter_value=="python":
                filter_value = "pypi"
            elif filter_value=="r":
                filter_value = "cran"

        if filter_attribute == "tags":
            q = q.filter(Package.tags.has_key(filter_value))        
        else:
            attr = getattr(Package, filter_attribute)
            q = q.filter(attr==filter_value)        

    q = q.order_by(Package.num_downloads.desc())
    q = q.limit(page_size)

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




q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.requires_files != None)
update_registry.register(Update(
    job=PypiPackage.set_host_deps,
    query=q,
    queue_id=5
))


q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.import_name == None)
update_registry.register(Update(
    job=PypiPackage.set_import_name,
    query=q,
    queue_id=1
))






q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.requires_files == None)
update_registry.register(Update(
    job=PypiPackage.set_requires_files,
    query=q,
    queue_id=6
))



q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.api_raw == None)
update_registry.register(Update(
    job=PypiPackage.set_api_raw,
    query=q,
    queue_id=4
))


q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.setup_py == None)
update_registry.register(Update(
    job=PypiPackage.set_setup_py,
    query=q,
    queue_id=2
))


q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.setup_py != None)
q = q.filter(PypiPackage.setup_py_import_name == None)
update_registry.register(Update(
    job=PypiPackage.set_setup_py_import_name,
    query=q,
    queue_id=3
))


q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.tags == None)
update_registry.register(Update(
    job=PypiPackage.set_tags,
    query=q,
    queue_id=2
))



q = db.session.query(CranPackage.id)
q = q.filter(~CranPackage.downloads.has_key('last_month'))
update_registry.register(Update(
    job=CranPackage.set_num_downloads_since,
    query=q,
    queue_id=7
))


q = db.session.query(CranPackage.id)
update_registry.register(Update(
    job=CranPackage.set_host_reverse_deps,
    query=q,
    queue_id=8
))


q = db.session.query(CranPackage.id)
update_registry.register(Update(
    job=CranPackage.save_host_contributors,
    query=q,
    queue_id=8
))

q = db.session.query(PypiPackage.id)
update_registry.register(Update(
    job=PypiPackage.save_host_contributors,
    query=q,
    queue_id=8
))

q = db.session.query(Package.id)
update_registry.register(Update(
    job=Package.save_host_contributors,
    query=q,
    queue_id=8
))

q = db.session.query(Package.id)
update_registry.register(Update(
    job=Package.save_all_people,
    query=q,
    queue_id=8
))

q = db.session.query(PypiPackage.id)
update_registry.register(Update(
    job=PypiPackage.set_igraph_data,
    query=q,
    queue_id=8,
    shortcut_fn=shortcut_igraph_data_dict
))

q = db.session.query(CranPackage.id)
update_registry.register(Update(
    job=CranPackage.set_igraph_data,
    query=q,
    queue_id=8,
    shortcut_fn=shortcut_igraph_data_dict
))


# i do not understand why, but this does not work in RQ, you must run in
# a single dyno with --no-rq flag set...takes a good 30min :/
q = db.session.query(Person.id)
q = q.filter(Person.impact == None)
update_registry.register(Update(
    job=Person.set_impact,
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

q = db.session.query(Person.id)
q = q.filter(Person.github_about == text("'null'"))  # jsonb null, not sql NULL
update_registry.register(Update(
    job=Person.set_github_about,
    query=q,
    queue_id=8
))


q = db.session.query(CranPackage.id)
q = q.filter(CranPackage.tags == None)
update_registry.register(Update(
    job=CranPackage.set_tags,
    query=q,
    queue_id=8
))

q = db.session.query(Package.id)
q = q.filter(Package.github_owner != None)
q = q.filter(Package.github_contributors == None)
update_registry.register(Update(
    job=Package.set_github_contributors,
    query=q,
    queue_id=8
))


q = db.session.query(GithubRepoDeplines.id)
q = q.filter(GithubRepoDeplines.dependency_lines != None)
q = q.filter(GithubRepoDeplines.language == 'python')
q = q.filter(GithubRepoDeplines.pypi_dependencies == None)
update_registry.register(Update(
    job=GithubRepoDeplines.set_pypi_dependencies,
    query=q,
    queue_id=8,
    shortcut_fn=shortcut_get_pypi_package_names
))


q = db.session.query(Package.id)
q = q.filter(Package.github_contributors != None)
q = q.filter(Package.num_commits == None)
update_registry.register(Update(
    job=Package.set_num_committers_and_commits,
    query=q,
    queue_id=8
))

q = db.session.query(GithubRepo.id)
q = q.filter(GithubRepo.named_deps == None)
q = q.filter(GithubRepo.language == 'python')
update_registry.register(Update(
    job=GithubRepo.set_named_deps,
    query=q,
    queue_id=9
))


q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.pagerank_percentile == None)
update_registry.register(Update(
    job=PypiPackage.set_all_percentiles,
    query=q,
    queue_id=9,
    shortcut_fn=PypiPackage.shortcut_percentile_refsets
))

q = db.session.query(CranPackage.id)
q = q.filter(CranPackage.pagerank_percentile == None)
update_registry.register(Update(
    job=CranPackage.set_all_percentiles,
    query=q,
    queue_id=9,
    shortcut_fn=CranPackage.shortcut_percentile_refsets
))


q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.impact == None)
update_registry.register(Update(
    job=PypiPackage.set_impact,
    query=q,
    queue_id=9,
    shortcut_fn=PypiPackage.shortcut_impact_maxes
))

q = db.session.query(CranPackage.id)
# q = q.filter(CranPackage.impact == None)
update_registry.register(Update(
    job=CranPackage.set_impact,
    query=q,
    queue_id=9,
    shortcut_fn=CranPackage.shortcut_impact_maxes
))















