import os
import math
from collections import defaultdict

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import func
from sqlalchemy import sql
import igraph
import nltk
from nltk.corpus import words
import numpy

from app import db
from models import github_api
from models.person import get_or_make_person
from models.contribution import Contribution
from models.rev_dep_node import RevDepNode
from jobs import update_registry
from jobs import Update
from util import truncate
from providers import full_text_source


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
    is_academic = db.Column(db.Boolean)

    num_citations_by_source = db.Column(JSONB)
    is_distinctive_name = db.Column(db.Boolean)

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

    impact = db.Column(db.Float)
    impact_rank = db.Column(db.Integer)

    num_committers = db.Column(db.Integer)
    num_commits = db.Column(db.Integer)
    num_authors = db.Column(db.Integer)

    inactive = db.Column(db.Text)

    rev_deps_tree = db.Column(JSONB)
    credit = db.Column(JSONB)


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


    def to_dict(self, full=True):
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
            "impact": self.impact,
            "rev_deps_tree": self.tree,
            "citations": self.citations_dict,

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

            "impact": self.impact,

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

        ret["contributions"] = defaultdict(list)
        for c in self.contributions:
            ret["contributions"][c.role].append(u"{}: {}".format(
                c.percent, c.person.display_name))

        for role in ret["contributions"]:
            ret["contributions"][role].sort(reverse=True)


        ret["credit"] = []
        for p in self.contributors_with_credit():
            ret["credit"].append(
                u"{share}: {name} ({id})".format(
                    share = p.credit, 
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
    def host_url(self):
        # this needs to be overridden, because it depends on whether we've
        # got a pypi or cran package
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

    def set_credit(self):
        people = self.contributors_with_credit()
        credit_dict = {}
        for person in people:
            credit_dict[int(person.id)] = person.credit
        self.credit = credit_dict

    def get_credit_for_person(self, person_id):
        return self.credit[str(person_id)]


    @property
    def has_github_commits(self):
        return self.max_github_commits > 0

    @property
    def max_github_commits(self):
        if len(self.contributions) == 0:
            return 0

        all_commits = [c.quantity for c in self.contributions 
                            if c.quantity and c.role=="github_contributor"]
        if not all_commits:
            return None

        return max(all_commits)


    def contributors_with_credit(self):
        people_for_contributions = self.all_people
        author_committers = []
        non_author_committers = []

        # if no github contributors, split cred equally among all authors
        # if github contributors, give contributions tied with maximum github contribution
        #  by making them a virtual committer with that many commits
        for person in people_for_contributions:
            person.credit = 0  # initialize

            if person.has_role_on_project("author", self.id):
                if self.has_github_commits:
                    # print u"{} is an author committer".format(person.name)
                    author_committers += [person]
                else:
                    # print u"{} is an author and there are no committers".format(person.name)
                    equal_author_share = float(1)/len(self.all_authors)                    
                    person.credit += equal_author_share

            elif person.has_role_on_project("github_contributor", self.id):
                # print u"{} is a non-author committer".format(person.name)
                non_author_committers += [person]


        # give all non-author committers their number of real commits
        for person in non_author_committers:
            person.num_counting_commits = person.num_commits_on_project(self.id)

        # give all virtual committers the max number of commits
        for person in author_committers:
            person.num_counting_commits = self.max_github_commits

        # calc how many commits were handed out, real + virtual
        total_author_and_nonauthor_commits = 0
        author_and_nonauthor_commmiters = non_author_committers + author_committers
        for person in author_and_nonauthor_commmiters:
            total_author_and_nonauthor_commits += person.num_counting_commits

        # assign credit to be the fraction of commits they have out of total
        # print "total_author_and_nonauthor_commits", total_author_and_nonauthor_commits
        for person in author_and_nonauthor_commmiters:
            person.credit = float(person.num_counting_commits) / total_author_and_nonauthor_commits
            # print u"{} has with {} commits, {} credit".format(
            #     person.name, person.num_commits, person.credit)

        # finally, handle github owners by giving them a little boost
        for person in people_for_contributions:
            if person.has_role_on_project("github_owner", self.id):
                person.credit += 0.01

        people_for_contributions.sort(key=lambda x: x.credit, reverse=True)

        # for person in people_for_contributions:
        #     print u"{credit}: {name} has contribution".format(
        #         name = person.name, 
        #         credit = round(person.credit, 3)
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

    def set_is_distinctive_name(self):
        nltk.download('words')  # only downloads the first time, so can safely put here

        word_list = words.words()
        if self.project_name.lower() in word_list:
            return False
        return True

    @property
    def citations_dict(self):
        citations_dict = self.set_num_citations_by_source()
        response_dict = defaultdict(dict)
        sources = [
            full_text_source.Pmc,
            full_text_source.Arxiv,
            full_text_source.Citeseer,
        ]
        for source_class in sources:
            source = source_class()
            response_dict[source.name] = {
                "count": citations_dict[source.name], 
                "url": source.query_url(self.full_text_query)
                }
        return response_dict

    @property
    def full_text_query(self):
        queries = []

        # add the cran or pypi url to start with
        host_url = self.host_url.replace("https://", "").replace("http://", "")
        queries.append('"{}"'.format(host_url))

        # then github url if we know it
        if self.github_owner:
            github_url = '"github.com/{}/{}"'.format(self.github_owner, self.github_repo_name)
            queries.append(github_url)

        # also look up its project name if is unique
        if self.is_distinctive_name:
            queries.append('"{}"'.format(self.project_name))
        else:
            print "{} isn't a rare package name, so not looking up by name".format(self.project_name)

        query = " OR ".join(queries)
        print "query", query
        return query

    def set_num_citations_by_source(self):
        if not self.num_citations_by_source:
            self.num_citations_by_source = {}

        sources = [
            full_text_source.Pmc,
            full_text_source.Arxiv,
            full_text_source.Citeseer,
        ]

        self.num_citations = 0
        for source_class in sources:
            source = source_class()
            num_found = source.run_query(self.full_text_query)
            self.num_citations_by_source[source.name] = num_found
            self.num_citations += num_found

        return self.num_citations_by_source


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


    @classmethod
    def shortcut_impact_rank(cls):
        print "getting the lookup for ranking impact...."
        q = db.session.query(cls.id)
        q = q.order_by(cls.impact.desc())  # the important part :)
        rows = q.all()

        impact_rank_lookup = {}
        ids_sorted_by_impact = [row[0] for row in rows]
        for my_id in ids_sorted_by_impact:
            zero_based_rank = ids_sorted_by_impact.index(my_id)
            impact_rank_lookup[my_id] = zero_based_rank + 1

        return impact_rank_lookup


    def set_impact_rank(self, impact_rank_lookup):
        self.impact_rank = impact_rank_lookup[self.id]
        print "self.impact_rank", self.impact_rank


    @classmethod
    def shortcut_impact_maxes(cls):
        print "getting the maxes for calculating the impact...."
        q = db.session.query(
            func.max(cls.num_downloads),
            func.max(cls.pagerank),
            func.max(cls.num_citations)
        )
        row = q.first()

        maxes_dict = {}
        maxes_dict["num_downloads"] = row[0]
        maxes_dict["pagerank"] = row[1]
        maxes_dict["num_citations"] = row[2]

        print "maxes_dict=", maxes_dict

        return maxes_dict


    def set_impact(self, maxes_dict):

        score_components = []

        if self.pagerank:
            log_pagerank = math.log10(float(self.pagerank)/maxes_dict["pagerank"])
            if log_pagerank != None:
                score_components.append(log_pagerank)
        if self.num_downloads:
            log_num_downloads = math.log10(float(self.num_downloads)/maxes_dict["num_downloads"])
            if log_num_downloads != None:
                score_components.append(log_num_downloads)

        if score_components:
            offset_to_recenter = 5
            my_mean = numpy.mean(score_components) + offset_to_recenter
        else:
            my_mean = None
        
        self.impact = my_mean
        print u"self.impact for {} is {}".format(self.id, self.impact)


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
            generation=0,
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


















