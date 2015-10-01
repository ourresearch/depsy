import os
from collections import defaultdict

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import func
from sqlalchemy import sql
import igraph
import numpy

from app import db
from models import github_api
from models.person import get_or_make_person
from models.contribution import Contribution
from models.rev_dep_node import RevDepNode
from jobs import update_registry
from jobs import Update
from util import truncate
from providers.pubmed_api import get_pmids_from_query




class Package(db.Model):
    id = db.Column(db.Text, primary_key=True)
    host = db.Column(db.Text)
    project_name = db.Column(db.Text)
    import_name = db.Column(db.Text)
    unique_import_name = db.Column(db.Boolean)
    setup_py_import_name = db.Column(db.Text)

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

    @property
    def language(self):
        return "unknown"

    @property
    def impact(self):
        # this needs to change once we get a db col called impact...
        try:
            return self.sort_score * 100
        except TypeError:
            return 0

    def to_dict(self, full=True):
        #return {"hello": "world"}
        ret = {
            "name": self.project_name,
            "as_snippet": self.as_snippet,
            #"contributions": [c.to_dict() for c in self.contributions],
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
            "impact": self.impact,
            "rev_deps_tree": self.tree,

            # current implementation requires api_raw, so slows down db because deferred
            # "source_url": self.source_url,  

            "summary": self.summary,
            "tags": self.tags
        }
        # if full:
        #     ret["contributions"] = [c.to_dict() for c in self.contributions]

        return ret


    @property
    def tree(self):
        return self.rev_deps_tree


    @property
    def as_snippet(self):
        ret = {
            "_host_url": self.host_url,
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

    @property
    def as_snippet_with_people(self):
        ret = self.as_snippet

        # distinct_people = set([c.person.name for c in self.contributions])
        # ret["people"] = list([name for name in distinct_people if name])

        # ret["contributions"] = defaultdict(list)
        # for c in self.contributions:
        #     ret["contributions"][c.role].append(u"{}: {}".format(
        #         c.percent, c.person.display_name))

        # for role in ret["contributions"]:
        #     ret["contributions"][role].sort(reverse=True)

        ret["fair_shares"] = []
        for p in self.contributors_with_fair_shares():
            ret["fair_shares"].append(
                u"{share}: {name} ({id})".format(
                    share = p.fair_share, 
                    name = p.display_name,
                    id = p.id
                ) 
            )

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

    def save_all_people(self):
        self.save_github_owners_and_contributors()
        self.save_host_contributors()

    def save_github_owners_and_contributors(self):
        self.save_github_contribs_to_db()
        self.save_github_owner_to_db()

    def save_host_contributors(self):
        # this needs to be overridden, because it depends on whether we've
        # got a pypi or cran package...they have diff metadata formats.
        raise NotImplementedError

    @property
    def all_people(self):
        people = list(set([c.person for c in self.contributions]))
        return people

    @property
    def all_authors(self):
        people = list(set([c.person for c in self.contributions if c.role=="author"]))
        return people

    @property
    def all_github_owners(self):
        people = list(set([c.person for c in self.contributions if c.role=="github_owner"]))
        return people


    @property
    def virtual_author_share(self):
        author_share = float(1)/len(self.all_authors)
        return author_share

    def get_fair_share_for_person(self, person_id):
        people = self.contributors_with_fair_shares()
        for person in people:
            if person.id == person_id:
                return person.fair_share
        return None

    def contributors_with_fair_shares(self):
        people_for_contributions = self.all_people
        virtual_committers = []
        real_committers = []

        # if no github contributors, split cred equally among all authors
        # if github contributors, give real contributions if they are a contributor
        # else make them a virtual committer so we can calculate mean contribution for them
        for person in people_for_contributions:
            person.fair_share = 0

            if person.has_role_on_project("github_owner", self.id):
                person.fair_share += 0.01

            if person.has_role_on_project("github_contributor", self.id):
                # print u"{} is a real committer".format(person.name)
                real_committers += [person]

            elif person.has_role_on_project("author", self.id):
                if self.num_commits:
                    # print u"{} is a virtual committer".format(person.name)
                    virtual_committers += [person]
                else:
                    # print u"{} is an author and there are no committers".format(person.name)
                    person.fair_share += self.virtual_author_share

        # give all real committers their number of real commits
        for person in real_committers:
            person.num_commits = person.num_commits_on_project(self.id)

        # give all virtual committers the mean number of commits
        num_real_commits = self.num_commits if self.num_commits else 0
        num_real_committers = self.num_committers if self.num_committers else 1
        mean_number_of_commits = float(num_real_commits) / num_real_committers
        for person in virtual_committers:
            person.num_commits = mean_number_of_commits

        # calc how many commits were handed out, real + virtual
        total_real_and_virtual_commits = 0
        real_and_virtual_commmiters = real_committers + virtual_committers
        for person in real_and_virtual_commmiters:
            total_real_and_virtual_commits += person.num_commits

        # assign fair share to be the fraction of commits they have out of total
        # print "total_real_and_virtual_commits", total_real_and_virtual_commits
        for person in real_and_virtual_commmiters:
            person.fair_share = float(person.num_commits) / total_real_and_virtual_commits
            # print u"{} has with {} commits, {} fair share".format(
            #     person.name, person.num_commits, person.fair_share)

        people_for_contributions.sort(key=lambda x: x.fair_share, reverse=True)

        # for person in people_for_contributions:
        #     print u"{fair_share}: {name} has contribution".format(
        #         name = person.name, 
        #         fair_share = round(person.fair_share, 3)
        #         )

        return people_for_contributions


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


    def set_num_committers_and_commits(self):
        if not self.set_github_contributors:
            return None
        try:
            self.num_committers = len(self.github_contributors)
            self.num_commits = sum([contrib["contributions"] for contrib in self.github_contributors])
        except TypeError:
            self.num_committers = 0
            self.num_commits = 0


    def _save_contribution(self, person, role, quantity=None, percent=None):
        print u"saving contribution {} for {}".format(role, person)
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
        self.set_num_committers_and_commits()
        

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


    def set_igraph_data(self, our_igraph_data):
        try:
            self.pagerank = our_igraph_data[self.project_name]["pagerank"]
            self.neighborhood_size = our_igraph_data[self.project_name]["neighborhood_size"]
            self.indegree = our_igraph_data[self.project_name]["indegree"]
            print "pagerank of {} is {}".format(self.project_name, self.pagerank)
        except KeyError:
            print "pagerank of {} was not calculated".format(self.project_name)
            self.pagerank = None
            self.neighborhood_size = None
            self.indegree = None
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
    def shortcut_percentile_refsets(cls):
        print "getting the percentile refsets...."
        ref_list = defaultdict(dict)
        q = db.session.query(
            cls.num_downloads,
            cls.pagerank,
            cls.num_citations
        )
        rows = q.all()

        ref_list["num_downloads"] = sorted([row[0] for row in rows if row[0] != None])
        ref_list["pagerank"] = sorted([row[1] for row in rows if row[1] != None])
        ref_list["num_citations"] = sorted([row[2] for row in rows if row[2] != None])

        return ref_list


    def _calc_percentile(self, refset, value):
        if value is None:  # distinguish between that and zero
            return None
         
        matching_index = refset.index(value)
        percentile = float(matching_index) / len(refset)
        return percentile

    def set_num_downloads_percentile(self, refset):
        self.num_downloads_percentile = self._calc_percentile(refset, self.num_downloads)

    def set_pagerank_percentile(self, refset):
        self.pagerank_percentile = self._calc_percentile(refset, self.pagerank)

    def set_num_citations_percentile(self, refset):
        self.num_citations_percentile = self._calc_percentile(refset, self.num_citations)

    def set_all_percentiles(self, refsets_dict):
        self.set_num_downloads_percentile(refsets_dict["num_downloads"])
        self.set_pagerank_percentile(refsets_dict["pagerank"])
        self.set_num_citations_percentile(refsets_dict["num_citations"])
        self.set_sort_score()

    @classmethod
    def shortcut_rev_deps_pairs(cls):
        NUM_TOP_NODES = 1000

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

        non_zero_pageranks = [row[2] for row in rows if row[2]]
        min_pagerank = min(non_zero_pageranks)

        for row in rows:
            my_name = row[0]
            child_name = row[1]
            child_pagerank = row[2]
            child_stars = row[3]

            if not child_pagerank:
                child_pagerank = min_pagerank

            rev_deps_by_package[my_name].append([
                child_name,
                child_pagerank,
                child_stars
            ])

        return rev_deps_by_package


    def set_rev_deps_tree(self, rev_deps_lookup):
        node = RevDepNode(
            parent=None,
            name=self.project_name,
            pagerank=self.pagerank,
            stars=None,
            root_pagerank=self.pagerank
        )
        node.is_root = True
        node.set_children(rev_deps_lookup)
        self.rev_deps_tree = node.to_dict()






def prep_summary(str):
    placeholder = "A nifty project."
    if not str:
        return placeholder
    elif str == "UNKNOWN":
        return placeholder
    else:
        return truncate(str)


def make_id(namespace, name):
    """
    pass a language name or host in with a name, get a Package.id str
    """

    namespace = namespace.lower()

    if namespace in ["cran", "pypi"]:
        return namespace + ":" + "name"

    elif namespace == "python":
        return "pypi:" + name

    elif namespace == "r":
        return "cran:" + name

    else:
        raise ValueError("Invalid namespace for package id")






def shortcut_igraph_data_dict():

    print "loading text dataset into igraph"
    our_graph = igraph.read("dep_nodes_ncol.txt", format="ncol", directed=True, names=True)

    print "loaded, now calculating..."
    our_vertice_names = our_graph.vs()["name"]
    our_pageranks = our_graph.pagerank(implementation="prpack")
    our_neighbourhood_size = our_graph.neighborhood_size(our_graph.vs(), mode="IN", order=100)
    our_indegree = our_graph.vs().indegree()

    print "reformating data into dict ..."
    global our_igraph_data
    our_igraph_data = {}
    for (i, name) in enumerate(our_vertice_names):
        our_igraph_data[name] = {
            "pagerank": our_pageranks[i],
            "neighborhood_size": our_neighbourhood_size[i],
            "indegree": our_indegree[i]
        }

    return our_igraph_data









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










