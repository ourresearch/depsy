from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import func
import numpy
import os
from collections import defaultdict

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

    num_depended_on = db.Column(db.Float)
    num_depended_on_percentile = db.Column(db.Float)
    num_downloads = db.Column(db.Integer)
    num_downloads_percentile = db.Column(db.Float)
    num_citations = db.Column(db.Integer)
    num_citations_percentile = db.Column(db.Float)
    num_stars = db.Column(db.Integer)
    num_stars_percentile = db.Column(db.Float)
    pagerank = db.Column(db.Float)
    neighborhood_size = db.Column(db.Float)
    indegree = db.Column(db.Float)
    summary = db.Column(db.Text)

    sort_score = db.Column(db.Float)

    num_committers = db.Column(db.Integer)
    num_commits = db.Column(db.Integer)
    num_authors = db.Column(db.Integer)

    inactive = db.Column(db.Text)


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
            "num_citations": self.num_citations,
            "num_citations_percentile": self.num_citations_percentile,
            "num_commits": self.num_commits,
            "num_committers": self.num_committers,
            "num_depended_on": self.num_depended_on,
            "num_depended_on_percentile": self.num_depended_on_percentile,
            "num_downloads_percentile": self.num_downloads_percentile,
            "num_stars": self.num_stars,
            "num_stars_percentile": self.num_stars_percentile,
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
        raise NotImplementedError

    @property
    def _as_package_snippet(self):
        ret = {
            "name": self.project_name,
            "language": None,

            "sort_score": self.sort_score,
            "impact": self.sort_score * 100,

            "pagerank": self.pagerank,

            #  name bug
            "pagerank_percentile": self.num_depended_on_percentile,

            "num_downloads": self.num_downloads,
            "num_downloads_percentile": self.num_downloads_percentile,

            "num_stars": self.num_stars,
            "num_stars_percentile": self.num_stars_percentile,

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
            self.num_stars_percentile,
            self.num_citations_percentile,
            self.num_depended_on_percentile]
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

    def set_depended_on(self):
        global our_graph

        try:
            this_vertex = our_graph.vs.find(self.project_name)
            num_depended_on = our_graph.neighborhood_size(this_vertex, mode="OUT", order=999999)
            print "num_depended_on for {} is {}".format(self.project_name, num_depended_on)
        except ValueError:
            num_depended_on = 0
            print "no num_depended_on found for {}".format(self.project_name)
        self.num_depended_on = num_depended_on


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

        self.num_depended_on = self.pagerank
        self.set_all_percentiles()


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
    def _group_by_host(cls, rows, col_number):
        ret = {
            "pypi": [row[col_number] for row in rows if row[0]=="pypi" and row[col_number]!=None],
            "cran": [row[col_number] for row in rows if row[0]=="cran" and row[col_number]!=None]
        }

        return ret

    @classmethod
    def get_refsets(cls):
        q = db.session.query(
                cls.host, 
                cls.num_downloads, 
                cls.num_depended_on,
                cls.num_stars,
                cls.num_citations)
        rows = q.all()

        all_values = {}
        all_values["num_downloads"] = cls._group_by_host(rows, 1)
        all_values["num_depended_on"] = cls._group_by_host(rows, 2)
        all_values["num_stars"] = cls._group_by_host(rows, 3)
        all_values["num_citations"] = cls._group_by_host(rows, 4)

        refsets = defaultdict(dict)
        for refset_type in all_values:
            for host in all_values[refset_type]:
                values = all_values[refset_type][host]
                distinct_values = sorted(list(set(values)))
                num_distinct_values = len(distinct_values)
                percentiles = [float(i)/num_distinct_values for (i, value) in enumerate(distinct_values)]
                this_refset = zip(distinct_values, percentiles)
                refsets[refset_type][host] = this_refset
        return refsets


    def _calc_percentile(self, refset, value):
        if value == None:  # distinguish between that and zero
            return None

        # print "using refset of length", len(refset[self.host])
        # print "using refset last value", refset[self.host][len(refset[self.host]) - 1]
        # print "looking up", value
        for (cutoff, percentile) in refset[self.host]:
            if cutoff >= value:
                # print "hit it! at cutoff", cutoff
                return percentile
        # print "didn't find anything"
        return 99.9999

    def set_num_downloads_percentile(self):
        global refsets
        print "here in download percentile"
        self.num_downloads_percentile = self._calc_percentile(refsets["num_downloads"], self.num_downloads)
        print "that's all folks"

    def set_num_depended_on_percentile(self):
        global refsets
        self.num_depended_on_percentile = self._calc_percentile(refsets["num_depended_on"], self.num_depended_on)

    def set_num_star_percentile(self):
        global refsets
        self.num_stars_percentile = self._calc_percentile(refsets["num_stars"], self.num_stars)

    def set_num_citations_percentile(self):
        global refsets
        self.num_citations_percentile = self._calc_percentile(refsets["num_citations"], self.num_citations)

    def set_all_percentiles(self):
        self.set_num_downloads_percentile()
        self.set_num_depended_on_percentile()
        self.set_num_star_percentile()
        self.set_num_citations_percentile()
        self.set_sort_score()




def prep_summary(str):
    placeholder = "A nifty project."
    if not str:
        return placeholder
    elif str == "UNKNOWN":
        return placeholder
    else:
        return truncate(str)



def get_packages(sort="sort_score", filters=None):

    # not implemented yet
    return []

    if not sort.startswith("num_") and not sort == "sort_score":
        sort = "num_" + sort

    allowed_sorts = [
        "sort_score",
        "percentile",
        "num_downloads",
        "num_citations"
    ]

    if sort not in allowed_sorts:
        raise ValueError("'sort' arg is something we can't sort by.")

    sort_property = getattr(Package, sort)



    q = db.session.query(Package)
    q = q.order_by(sort_property.desc())
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
    refsets = Package.get_refsets()
    print "done loading data into memory"


q = db.session.query(Package.id)
q = q.filter(Package.num_depended_on_percentile != None)
q = q.filter(Package.num_downloads_percentile == None)
update_registry.register(Update(
    job=Package.set_num_downloads_percentile,
    query=q,
    queue_id=8
))


q = db.session.query(Package.id)
q = q.filter(Package.sort_score == None)

update_registry.register(Update(
    job=Package.set_all_percentiles,
    query=q,
    queue_id=8
))










