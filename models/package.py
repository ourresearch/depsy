import os
from collections import defaultdict

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import func
from sqlalchemy import sql
import numpy

from app import db
from models import github_api
from models.person import get_or_make_person
from models.contribution import Contribution
from jobs import update_registry
from jobs import Update
from util import truncate
from providers.pubmed_api import get_pmids_from_query




class Package(db.Model):
    id = db.Column(db.Text, primary_key=True)
    host = db.Column(db.Text)
    project_name = db.Column(db.Text)

    github_owner = db.Column(db.Text)
    github_repo_name = db.Column(db.Text)
    github_api_raw = db.deferred(db.Column(JSONB))
    github_contributors = db.deferred(db.Column(JSONB))

    api_raw = db.deferred(db.Column(JSONB))
    downloads = db.deferred(db.Column(MutableDict.as_mutable(JSONB)))
    all_r_reverse_deps = db.deferred(db.Column(JSONB))       
    tags = db.deferred(db.Column(JSONB))
    proxy_papers = db.deferred(db.Column(db.Text))

    pmc_mentions = db.Column(JSONB)
    host_reverse_deps = db.deferred(db.Column(JSONB))

    github_reverse_deps = db.deferred(db.Column(JSONB))
    dependencies = db.deferred(db.Column(JSONB))
    bucket = db.deferred(db.Column(MutableDict.as_mutable(JSONB)))
    requires_files = db.deferred(db.Column(MutableDict.as_mutable(JSONB)))
    setup_py = db.deferred(db.Column(db.Text))
    setup_py_hash = db.deferred(db.Column(db.Text))

    num_downloads = db.Column(db.Integer)
    num_downloads_percentile = db.Column(db.Float)
    num_citations = db.Column(db.Integer)
    num_citations_percentile = db.Column(db.Float)
    num_stars = db.Column(db.Integer)
    pagerank = db.Column(db.Float)
    pagerank_percentile = db.Column(db.Float)

    neighborhood_size = db.Column(db.Float)
    indegree = db.Column(db.Float)
    summary = db.Column(db.Text)

    sort_score = db.Column(db.Float)

    num_committers = db.Column(db.Integer)
    num_commits = db.Column(db.Integer)
    num_authors = db.Column(db.Integer)

    inactive = db.Column(db.Text)

    rev_deps_tree = db.Column(JSONB)


    contributions = db.relationship(
        'Contribution',
        # lazy='subquery',
        cascade="all, delete-orphan",
        backref="package"
    )



    __mapper_args__ = {
        'polymorphic_on': host,
        'with_polymorphic': '*'
    }


    def __repr__(self):
        return u'<Package {name}>'.format(
            name=self.id)


    def to_dict(self, full=True):
        ret = {
            "as_snippet": self.as_snippet,
            "contributions": [c.to_dict() for c in self.contributions],
            "github_owner": self.github_owner,
            "github_repo_name": self.github_repo_name,
            "host": self.host,
            "indegree": self.indegree,
            "neighborhood_size": self.neighborhood_size,
            "num_authors": self.num_authors,
            "num_commits": self.num_commits,
            "num_committers": self.num_committers,
            "num_citations": self.num_citations,
            "num_citations_percentile": self.num_citations_percentile,
            "pagerank": self.pagerank,
            "pagerank_percentile": self.pagerank_percentile,
            "num_downloads": self.num_downloads,
            "num_downloads_percentile": self.num_downloads_percentile,
            "num_stars": self.num_stars,
            "sort_score": self.sort_score,
            "impact": self.sort_score * 100,

            # current implementation requires api_raw, so slows down db because deferred
            # "source_url": self.source_url,  

            "summary": self.summary,
            "tags": self.tags
        }
        # if full:
        #     ret["contributions"] = [c.to_dict() for c in self.contributions]

        return ret


    @property
    def as_snippet(self):
        ret = {
            "name": self.project_name,
            "language": self.language,

            "sort_score": self.sort_score,
            "impact": self.sort_score * 100,

            "pagerank": self.pagerank,
            "pagerank_percentile": self.pagerank_percentile,

            "num_downloads": self.num_downloads,
            "num_downloads_percentile": self.num_downloads_percentile,

            "num_citations": self.num_citations,
            "num_citations_percentile": self.num_citations_percentile,

            "summary": prep_summary(self.summary)
        }
        return ret

    @classmethod
    def valid_package_names(cls, module_names):
        """
        this will normally be called by subclasses, to filter by specific package hosts
        """
        lowercase_module_names = [n.lower() for n in module_names]
        q = db.session.query(cls.project_name)
        q = q.filter(func.lower(cls.project_name).in_(lowercase_module_names))
        response = [row[0] for row in q.all()]
        return response

    def test(self):
        print "{}: I'm a test!".format(self)



    def save_github_owners_and_contributors(self):
        self.save_github_contribs_to_db()
        self.save_github_owner_to_db()

    def save_host_contributors(self):
        # this needs to be overridden, because it depends on whether we've
        # got a pypi or cran package...they have diff metadata formats.
        raise NotImplementedError

    def save_github_contribs_to_db(self):
        if isinstance(self.github_contributors, dict):
            # it's an error resp from the API, doh.
            return None

        if self.github_contributors is None:
            return None

        total_contributions_count = sum([c['contributions'] for c in self.github_contributors])
        for github_contrib in self.github_contributors:
            person = get_or_make_person(github_login=github_contrib["login"])
            percent_total_contribs = round(
                github_contrib["contributions"] / float(total_contributions_count) * 100,
                3
            )
            self._save_contribution(
                person,
                "github_contributor",
                quantity=github_contrib["contributions"],
                percent=percent_total_contribs
            )
        self.num_github_committers = len(self.github_contributors)


    def save_github_owner_to_db(self):
        if not self.github_owner:
            return False

        person = get_or_make_person(github_login=self.github_owner)
        self._save_contribution(person, "github_owner")


    def _save_contribution(self, person, role, quantity=None, percent=None):
        extant_contrib = self.get_contribution(person.id, role)
        if extant_contrib is None:

            # make the new contrib.
            # there's got to be a better way to make this args thing...
            kwargs_dict = {
                "role": role
            }
            if quantity is not None:
                kwargs_dict["quantity"] = quantity
            if percent is not None:
                kwargs_dict["percent"] = percent

            new_contrib = Contribution(**kwargs_dict)

            # set the contrib in its various places.
            self.contributions.append(new_contrib)
            person.contributions.append(new_contrib)
            db.session.merge(person)


    def get_contribution(self, person_id, role):
        for contrib in self.contributions:
            if contrib.person.id == person_id and contrib.role == role:
                return contrib

        return None

    def set_github_contributors(self):
        self.github_contributors = github_api.get_repo_contributors(
            self.github_owner,
            self.github_repo_name
        )
        print "found github contributors", self.github_contributors

    def set_github_repo_id(self):
        # override in subclass
        raise NotImplementedError

    def set_tags(self):
        # override in subclass
        raise NotImplementedError

    def set_sort_score(self):
        scores = [
            self.num_downloads_percentile,
            self.num_citations_percentile,
            self.pagerank_percentile
            ]
        non_null_scores = [s for s in scores if s!=None]
        self.sort_score = numpy.mean(non_null_scores)
        print "sort score for {} is {}".format(self.id, self.sort_score)

    def set_pmc_mentions(self):

        # nothing to do here at the moment
        if not self.github_owner:
            return None

        # don't start with http:// for now because then can get urls that include www
        github_url_query = "github.com/{}/{}".format(self.github_owner, self.github_repo_name)
        new_pmids_set = set(get_pmids_from_query(github_url_query))

        self.pmc_mentions = new_pmids_set
        return self.pmc_mentions


    def set_pagerank(self):
        global our_igraph_data

        try:
            self.pagerank = our_igraph_data[self.project_name]["pagerank"]
            self.neighborhood_size = our_igraph_data[self.project_name]["neighborhood_size"]
            self.indegree = our_igraph_data[self.project_name]["indegree"]
            print "pagerank of {} is {}".format(self.project_name, self.pagerank)
        except KeyError:
            print "pagerank of {} is not defined".format(self.project_name)
            self.pagerank = 0
            self.neighborhood_size = 0
            self.indegree = 0

        self.pagerank = self.pagerank
        # self.set_all_percentiles()


    def refresh_github_ids(self):
        if not self.github_owner:
            return None

        self.github_api_raw = github_api.get_repo_data(self.github_owner, self.github_repo_name)
        try:
            (self.github_owner, self.github_repo_name) = self.github_api_raw["full_name"].split("/")
        except KeyError:
            self.github_owner = None
            self.github_repo_name = None




    @classmethod
    def get_ref_list(cls):
        ref_list = defaultdict(dict)
        for host_class in [PypiPackage, CranPackage]:
            host_name = host_class.__name__
            q = db.session.query(
                    host_class.num_downloads, 
                    host_class.pagerank,
                    host_class.num_citations
                    )
            rows = q.all()

            ref_list["num_downloads"][host_name] = sorted([row[0] for row in rows if row[0] != None])
            ref_list["pagerank"][host_name] = sorted([row[1] for row in rows if row[1] != None])
            ref_list["num_citations"][host_name] = sorted([row[2] for row in rows if row[2] != None])

        return ref_list


    def _calc_percentile(self, ref_list, value):
        if value == None:  # distinguish between that and zero
            return None
         
        my_ref_list = ref_list[self.__class__.__name__]  #ideally put this in subclasses so don't need this hack
        matching_index = my_ref_list.index(value)
        percentile = float(matching_index) / len(my_ref_list)
        return percentile


    def set_num_downloads_percentile(self):
        global ref_lists
        self.num_downloads_percentile = self._calc_percentile(ref_lists["num_downloads"], self.num_downloads)

    def set_pagerank_percentile(self):
        global ref_lists
        self.pagerank_percentile = self._calc_percentile(ref_lists["pagerank"], self.pagerank)

    def set_num_citations_percentile(self):
        global ref_lists
        self.num_citations_percentile = self._calc_percentile(ref_lists["num_citations"], self.num_citations)

    def set_all_percentiles(self):
        self.set_num_downloads_percentile()
        self.set_pagerank_percentile()
        self.set_num_citations_percentile()
        self.set_sort_score()

    @classmethod
    def shortcut_rev_deps_pairs(cls):

        command = """select package, 
                        used_by, 
                        pagerank, 
                        (coalesce((github_repo.api_raw->>'stargazers_count')::int, 0) 
                            + coalesce(package.num_stars, 0)) as num_stars
                    from dep_nodes_ncol_{host}_reverse
                    left outer join github_repo 
                        on dep_nodes_ncol_{host}_reverse.used_by = 'github:' || github_repo.id
                    left outer join package 
                        on dep_nodes_ncol_{host}_reverse.used_by = package.project_name""".format(
                            host=cls.class_host)

        rev_deps_by_package = defaultdict(list)
        res = db.session.connection().execute(sql.text(command))
        rows = res.fetchall()

        pageranks = [row[2] for row in rows if row[2] is not None]
        min_pagerank = min(pageranks)

        for row in rows:
            package_name = row[0]
            used_by = row[1]
            my_pagerank = row[2]
            my_stars = row[3]

            if my_pagerank is None:
                my_pagerank = min_pagerank

            rev_deps_by_package[package_name].append({
                "used_by": used_by,
                "pagerank": my_pagerank,
                "stars": my_stars
            })

        ret = defaultdict(dict)
        for package_name, package_rev_deps in rev_deps_by_package.iteritems():

            # sort in place by pagerank
            package_rev_deps.sort(key=lambda x: (x["pagerank"], x["stars"]), reverse=True)
            best_rev_deps = package_rev_deps[0:2]  # top 2
            ret[package_name] = best_rev_deps

        return ret

    def set_rev_deps_tree(self, rev_deps_lookup):
        outbox = set()
        depth = 1
        inbox = [(self.project_name, depth)]
        while len(inbox):
            (my_package_name, depth) = inbox.pop()
            my_package_rev_deps = rev_deps_lookup[my_package_name]
            for rev_dep_dict in my_package_rev_deps:

                if rev_dep_dict["used_by"].startswith("github:"):
                    # this is a leaf node, no need to keep looking for rev deps
                    pass
                else:
                    # print "adding this to the inbox", rev_dep_dict["used_by"]
                    inbox.append((rev_dep_dict["used_by"], depth+1))

                node = (
                    depth,
                    my_package_name,
                    rev_dep_dict["used_by"],
                    rev_dep_dict["pagerank"], 
                    rev_dep_dict["stars"]
                )
                outbox.add(node)

        self.rev_deps_tree = list(outbox)
        self.rev_deps_tree.sort(key=lambda x: (x[0], x[1].lower(), x[2].lower())) #by depth

        print "found reverse dependency tree!"
        for node in self.rev_deps_tree:
            print node

        return self.rev_deps_tree




def prep_summary(str):
    placeholder = "A nifty project."
    if not str:
        return placeholder
    elif str == "UNKNOWN":
        return placeholder
    else:
        return truncate(str)



def get_packages(sort="sort_score", filters=None):



    q = db.session.query(Package)
    q = q.order_by(Package.pagerank.desc())
    q = q.order_by(Package.num_downloads.desc())

    q = q.limit(25)

    ret = q.all()
    return ret




#
######## igraph
#our_igraph_data = None
#
#q = db.session.query(PypiPackage.id)
#q = q.filter(PypiPackage.pagerank == None)
#update_registry.register(Update(
#    job=PypiPackage.set_pagerank,
#    query=q,
#    queue_id=5
#))
#
#q = db.session.query(CranPackage.id)
#q = q.filter(CranPackage.pagerank == None)
#update_registry.register(Update(
#    job=CranPackage.set_pagerank,
#    query=q,
#    queue_id=5
#))
#
#
#def run_igraph(host="cran", limit=2):
#    import igraph
#
#    print "loading in igraph"
#    our_graph = igraph.read("dep_nodes_ncol.txt", format="ncol", directed=True, names=True)
#    print "loaded, now calculating"
#    our_vertice_names = our_graph.vs()["name"]
#    our_pageranks = our_graph.pagerank(implementation="prpack")
#    our_neighbourhood_size = our_graph.neighborhood_size(our_graph.vs(), mode="IN", order=100)
#    our_indegree = our_graph.vs().indegree()
#
#    print "now saving"
#    global our_igraph_data
#    our_igraph_data = {}
#    for (i, name) in enumerate(our_vertice_names):
#        our_igraph_data[name] = {
#            "pagerank": our_pageranks[i],
#            "neighborhood_size": our_neighbourhood_size[i],
#            "indegree": our_indegree[i]
#        }
#
#    method_name = "{}Package.set_pagerank".format(host.title())
#    update = update_registry.get(method_name)
#    update.run(
#        no_rq=True,
#        obj_id=None,
#        num_jobs=limit,
#        chunk_size=1000
#    )







# for all Packages, not just pypi
q = db.session.query(Package.id)
q = q.filter(Package.sort_score == None)

update_registry.register(Update(
    job=Package.set_sort_score,
    query=q,
    queue_id=2
))





# runs on all packages
q = db.session.query(Package.id)
q = q.filter(Package.github_owner != None)
q = q.filter(Package.pmc_mentions == None)

update_registry.register(Update(
    job=Package.set_pmc_mentions,
    query=q,
    queue_id=7
))




# runs on all packages
q = db.session.query(Package.id)
q = q.filter(Package.github_owner != None)
q = q.filter(Package.github_api_raw == None)

update_registry.register(Update(
    job=Package.refresh_github_ids,
    query=q,
    queue_id=7
))



##### get percentiles.  Needs stuff loaded into memory before they run

if os.getenv("LOAD_FROM_DB_BEFORE_JOBS", "False") == "True":
    print "loading data from db into memory"
    ref_lists = Package.get_ref_list()
    print "done loading data into memory"


q = db.session.query(Package.id)
q = q.filter(Package.pagerank_percentile != None)
q = q.filter(Package.num_downloads_percentile == None)
update_registry.register(Update(
    job=Package.set_num_downloads_percentile,
    query=q,
    queue_id=8
))


q = db.session.query(Package.id)
# q = q.filter(Package.sort_score == None)

update_registry.register(Update(
    job=Package.set_all_percentiles,
    query=q,
    queue_id=8
))










