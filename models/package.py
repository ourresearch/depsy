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
from models.person import Person
from models.person import get_or_make_person
from models.contribution import Contribution
from models.rev_dep_node import RevDepNode
from models.github_repo import GithubRepo
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
    tags = db.Column(JSONB)
    proxy_papers = db.deferred(db.Column(db.Text))
    is_academic = db.Column(db.Boolean)

    host_reverse_deps = db.deferred(db.Column(JSONB))

    github_reverse_deps = db.deferred(db.Column(JSONB))
    dependencies = db.deferred(db.Column(JSONB))
    bucket = db.deferred(db.Column(MutableDict.as_mutable(JSONB)))
    pmc_distinctiveness = db.deferred(db.Column(MutableDict.as_mutable(JSONB)))
    citeseer_distinctiveness = db.deferred(db.Column(MutableDict.as_mutable(JSONB)))
    ads_distinctiveness = db.deferred(db.Column(MutableDict.as_mutable(JSONB)))
    requires_files = db.deferred(db.Column(MutableDict.as_mutable(JSONB)))
    setup_py = db.deferred(db.Column(db.Text))
    setup_py_hash = db.deferred(db.Column(db.Text))

    impact = db.Column(db.Float)
    impact_percentile = db.Column(db.Float)
    impact_rank = db.Column(db.Integer)

    num_downloads = db.Column(db.Integer)
    num_downloads_percentile = db.Column(db.Float)
    num_downloads_score = db.Column(db.Float)
    pagerank = db.Column(db.Float)
    pagerank_percentile = db.Column(db.Float)
    pagerank_score = db.Column(db.Float)
    num_citations = db.Column(db.Integer)
    num_citations_percentile = db.Column(db.Float)
    num_citations_score = db.Column(db.Float)
    num_citations_by_source = db.Column(MutableDict.as_mutable(JSONB))

    neighborhood_size = db.Column(db.Float)
    indegree = db.Column(db.Float)
    eccentricity = db.Column(db.Float)
    closeness = db.Column(db.Float)
    betweenness = db.Column(db.Float)
    eigenvector_centrality = db.Column(db.Float)
    max_path_length = db.Column(db.Integer)
    avg_path_length = db.Column(db.Float)
    longest_path = db.Column(JSONB)
    avg_outdegree_of_neighbors = db.Column(db.Float)
    avg_pagerank_of_neighbors = db.Column(db.Float)
    higher_pagerank_neighbors = db.Column(JSONB)
    higher_pagerank_neighborhood_size = db.Column(db.Integer)
    academic_neighborhood_size = db.Column(db.Integer)

    num_stars = db.Column(db.Integer)
    summary = db.Column(db.Text)

    num_committers = db.Column(db.Integer)
    num_commits = db.Column(db.Integer)
    num_authors = db.Column(db.Integer)

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



    def to_dict(self, exclude=None):
        if exclude is None:
            exclude = []

        property_names = [
            "github_owner",
            "github_repo_name",
            "host",
            "impact_rank",
            "impact_percentile",
            "language",
            "indegree",
            "neighborhood_size",
            "num_authors",
            "num_commits",
            "num_committers",
            "num_stars",
            "impact",
            "citations_dict",
            "tree",
            "top_neighbors",
            "is_academic",
            "summary",
            "tags",
            "subscores",
            "contribs",
            "top_contribs"
        ]

        ret = {}
        for property_name in property_names:
            if property_name not in exclude:
                ret[property_name] = getattr(self, property_name)

        # special cases
        ret["name"] = self.project_name
        if self.credit:
            ret["num_contribs"] = len(self.credit)


        return ret



    @property
    def tree(self):
        return self.rev_deps_tree

    @property
    def as_snippet_without_people(self):
        return self.to_dict(exclude=["contribs", "top_contribs", "tree", "top_neighbors", "citations_dict"])

    @property
    def as_snippet(self):
        return self.to_dict(exclude=["contribs", "tree", "top_neighbors", "citations_dict"])

    @property
    def engagement(self):
        return self.num_stars

    @property
    def engagement_score(self):
        return 442

    @property
    def engagement_percentile(self):
        try:
            return self.num_stars / 100
        except TypeError:
            return None

    @property
    def subscores(self):
        ret = [
            {
                "name": "num_downloads",
                "score": self.display_num_downloads_score,
                "percentile": self.num_downloads_percentile,
                "val": self.num_downloads,
                "display_name": "Downloads",
                "icon": "fa-download"
            },
            {
                "name": "num_mentions",
                "score": self.display_num_citations_score,
                "percentile": self.num_citations_percentile,
                "val": self.num_citations,
                "display_name": "Citations",
                "icon": "fa-file-text-o"
            },
            {
                "name": "pagerank",
                "score": self.display_pagerank_score,
                "percentile": self.pagerank_percentile,
                "val": self.display_pagerank_score,
                "display_name": "Software reuse",
                "icon": "fa-recycle"
            }
        ]
        return ret


    @property
    def top_contribs(self):
        return self.contribs[0:5]

    @property
    def contribs(self):
        if not self.credit:
            return []

        person_ids_sorted_by_credit = sorted(self.credit, key=self.credit.get, reverse=True)

        ret = []
        for person_id in person_ids_sorted_by_credit:
            person_id = int(person_id)

            # query is v. fast, cos Persons are in the Session (in memory).
            person = Person.query.get(person_id)
            person_snippet = person.as_package_snippet
            person_snippet["person_package_credit"] = self.credit[str(person_id)]
            person_snippet["roles"] = []
            for contrib in self.contributions:
                if contrib.person_id == person_id:
                    person_snippet["roles"].append(contrib.as_snippet)

            ret.append(person_snippet)

        return ret



    @property
    def top_neighbors(self):
        num_top_nodes = 5

        command = """select p.id
                    from dep_nodes_ncol_{host}_reverse d, package p
                    where d.used_by = p.project_name
                    and d.package='{package_name}'
                    and p.host = '{host}'
                    order by coalesce(p.impact, p.impact, 0) desc, p.num_downloads
                    limit {limit}""".format(
                            package_name = self.project_name,
                            host = self.host,
                            limit = num_top_nodes
                            )

        # top_packages = db.session.query(Package).from_statement(command).all()
        # res = [package.as_snippet for package in top_packages]

        rows = db.session.connection().execute(sql.text(command)).fetchall()
        ids = [row[0] for row in rows]
        if ids:
            top_packages = db.session.query(Package).filter(Package.id.in_(ids))
        else:
            top_packages = []
        ret = [package.as_snippet_without_people for package in top_packages]

        command = """select g.id
                    from dep_nodes_ncol_{host}_reverse d, github_repo g
                    where d.package='{package_name}'
                    and d.used_by = 'github:' || g.id
                    order by coalesce((g.api_raw->>'stargazers_count')::int, 0) desc
                    limit {limit}""".format(
                            package_name = self.project_name,
                            host = self.host,
                            limit = num_top_nodes
                            )

        rows = db.session.connection().execute(sql.text(command)).fetchall()
        ids = [row[0] for row in rows]
        if ids:
            top_githubs = db.session.query(GithubRepo).filter(GithubRepo.id.in_(ids))
        else:
            top_githubs = []
        ret += [github_repo.as_snippet for github_repo in top_githubs]

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


    def dedup_people(self):
        all_people = self.all_people

        people_by_name = defaultdict(list)
        for person in all_people:
            if person.name:
                name_to_dedup = person.name.lower()
                people_by_name[name_to_dedup].append(person)

        for name, people_with_name in people_by_name.iteritems():
            if len(people_with_name) <= 1:
                # this name has no dups
                pass
            else:
                people_with_github = [p for p in people_with_name if p.github_login]
                people_with_no_github = [p for p in people_with_name if not p.github_login]

                # don't merge people with github together
                # so we only care about merging if there are people with no github
                if people_with_no_github:
                    if people_with_github:
                        # merge people with no github into first person with github
                        dedup_target = people_with_github[0]
                        people_to_merge = people_with_no_github
                    else:
                        # pick first person with no github as target, rest as mergees
                        dedup_target = people_with_no_github[0]
                        people_to_merge = people_with_no_github[1:]

                    print u"person we will marge into: {}".format(dedup_target.id)
                    print u"people to merge: {}".format([p.id for p in people_to_merge])
                    
                    for person_to_delete in people_to_merge:
                        contributions_to_change = person_to_delete.contributions
                        for contrib in contributions_to_change:
                            contrib.person = dedup_target
                            db.session.add(contrib)
                        print u"now going to delete {}".format(person_to_delete)
                        db.session.delete(person_to_delete)

                    # have to run set_credit on everything after this


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


    def get_sources_to_query(self):
        # i bet there is a better way to do this!! :)
        sources_to_query = [
                    full_text_source.Ads,
                    full_text_source.Pmc
                    # full_text_source.Arxiv,
                    # full_text_source.Citeseer,
                ]
        return sources_to_query

    def get_sources_to_return(self):
        # i bet there is a better way to do this!! :)
        sources_to_return = [
                    full_text_source.Ads,
                    full_text_source.Pmc
                    # full_text_source.Arxiv,
                    # full_text_source.Citeseer,
                ]
        return sources_to_return

    @property
    def citations_dict(self):
        citations_dict = self.num_citations_by_source
        response = []
        for source_class in self.get_sources_to_return():
            source = source_class()
            try:
                citation_count = citations_dict[source.name]
            except KeyError:
                citation_count = 0
            query = self.build_full_text_query(source)
            response.append({
                "name": source.name,
                "display_name": source.display_name,
                "count": citation_count, 
                "url": source.query_url(query)
                })
        return response


    def build_full_text_query(self, source):

        if self.host == "pypi":

            query = """
                (
                    (="import {name}" 
                    OR ="github com {name}" 
                    OR ="pypi python org {name}" 
                    OR ="available in the {name} project" 
                    OR ="{name} a community-developed" 
                    OR ="library {name}" 
                    OR ="libraries {name}" 
                    OR ="package {name}" 
                    OR ="packages {name}" 
                    OR ="{name} package" 
                    OR ="{name} packages" 
                    OR ="{name} library" 
                    OR ="{name} libraries" 
                    OR ="{name} python" 
                    OR ="{name} software" 
                    OR ="{name} api" 
                    OR ="{name} coded" 
                    OR ="{name} new open-source" 
                    OR ="{name} open-source" 
                    OR ="open source software {name}" 
                    OR ="{name} modeling frameworks" 
                    OR ="{name} modeling environment" 
                    OR ="modeling framework {name}" 
                    OR ="{name}: sustainable software" 
                    OR ="{name} component-based modeling framework")  
            """.format(name=self.project_name)  # missing last paren on purpose
        else:
            query = """
                (
                      (="github com {name}" 
                    OR ="web packages {name}" 
                    OR ="available in the {name} project" 
                    OR ="{name} a community-developed" 
                    OR ="{name} r library" 
                    OR ="{name} r libraries" 
                    OR ="r library {name}" 
                    OR ="r libraries {name}" 
                    OR ="{name} package" 
                    OR ="{name} packages" 
                    OR ="package {name}" 
                    OR ="packages {name}" 
                    OR ="{name} software"  
                    OR ="{name} api" 
                    OR ="{name} coded" 
                    OR ="{name} new open-source" 
                    OR ="{name} open-source" 
                    OR ="open source software {name}" 
                    OR ="{name} modeling frameworks" 
                    OR ="{name} modeling environment" 
                    OR ="modeling framework {name}" 
                    OR ="{name}: sustainable software" 
                    OR ="{name} component-based modeling framework")  
                """.format(name=self.project_name) # missing last paren on purpose

        # replace extra white space so is a shorter url, otherwise errors
        query = ' '.join(query.split())

        if source.__class__.__name__ == "Pmc":
            query += ' NOT AUTH:"{}"'.format(self.project_name)
        elif source.__class__.__name__ == "Ads":
            query += ' -author:"{}"'.format(self.project_name)
            # only arxiv
            # query += ' pub:arXiv'

        query += ")"
        return query



    def set_num_citations_by_source(self):
        if not self.num_citations_by_source:
            self.num_citations_by_source = {}

        for source_class in self.get_sources_to_query():

            if source_class.__name__ == "Pmc" and ("-" in self.project_name):
                # pmc can't do a query if a hyphen in the name, so just bail
                print "is a hyphen name, and pmc can't do those, returning zero citations"
                num_found = 0
            else:
                source = source_class()
                query = self.build_full_text_query(source)
                num_found = source.run_query(query)

            self.num_citations_by_source[source.name] = num_found
            print "num citations found", num_found

        # do this now so can check
        self.set_ads_distinctiveness()

        return self.num_citations_by_source


    def set_num_citations(self):
        self.num_citations = 0        

        self.num_citations_by_source = {}

        for source in ["pmc", "ads"]:
            add_citations = False
            if source=="pmc":
                try:
                    num_source_citations = self.pmc_distinctiveness["num_hits_raw"]
                except KeyError:
                    # no citations here
                    print "didn't collect citations for pmc, skipping"
                    continue

                if num_source_citations < 10:
                    add_citations = True
                else:
                    ratio = float(self.pmc_distinctiveness["num_hits_with_language"])/self.pmc_distinctiveness["num_hits_raw"]
                    print source, "ratio", ratio, num_source_citations
                    if self.host == "cran":
                        if ratio > 0.20:
                            add_citations = True
                    else:
                        if ratio > 0.27:
                            add_citations = True
            elif source=="ads":
                try:
                    num_source_citations = self.ads_distinctiveness["num_hits_raw"]
                except KeyError:
                    # no citations here
                    print "didn't collect citations for pmc, skipping"
                    continue

                if num_source_citations < 10:
                    add_citations = True
                else:
                    ratio = float(self.ads_distinctiveness["num_hits_with_language"])/self.ads_distinctiveness["num_hits_raw"]
                    print source, "ratio", ratio, num_source_citations
                    if self.host == "cran":
                        if ratio > 0.20:
                            add_citations = True
                    else:
                        if ratio > 0.20:
                            add_citations = True
            if add_citations:
                self.num_citations += num_source_citations
                self.num_citations_by_source[source] = num_source_citations

        print "num citations is ", self.num_citations
        return self.num_citations


    def set_pmc_distinctiveness(self):
        source = full_text_source.Pmc()
        self.pmc_distinctiveness = self.calc_distinctiveness(source)

    def set_citeseer_distinctiveness(self):
        source = full_text_source.Citeseer()
        self.citeseer_distinctiveness = self.calc_distinctiveness(source)

    def set_ads_distinctiveness(self):
        source = full_text_source.Ads()
        self.ads_distinctiveness = self.calc_distinctiveness(source)


    def calc_distinctiveness(self, source):
        distinctiveness = {}

        raw_query = self.build_full_text_query(source)

        num_hits_raw = source.run_query(raw_query)
        distinctiveness["num_hits_raw"] = num_hits_raw

        num_hits_with_language = source.run_query(self.distinctiveness_query_prefix + raw_query)
        distinctiveness["num_hits_with_language"] = num_hits_with_language
        
        if distinctiveness["num_hits_raw"] > 0:
            distinctiveness["ratio"] = float(distinctiveness["num_hits_with_language"])/distinctiveness["num_hits_raw"]
        else:
            distinctiveness["ratio"] = None

        print "{}: solo search finds {}, ratio is {}".format(
            self.project_name, 
            distinctiveness["num_hits_raw"],
            distinctiveness["ratio"]
            )
        return distinctiveness



    def set_igraph_data(self, our_igraph_data):
        try:
            self.pagerank = our_igraph_data[self.project_name]["pagerank"]
            self.neighborhood_size = our_igraph_data[self.project_name]["neighborhood_size"]
            self.indegree = our_igraph_data[self.project_name]["indegree"]
            self.eccentricity = our_igraph_data[self.project_name]["eccentricity"]
            self.closeness = our_igraph_data[self.project_name]["closeness"]  
            self.betweenness = our_igraph_data[self.project_name]["betweenness"]  
            self.eigenvector_centrality = our_igraph_data[self.project_name]["eigenvector_centrality"]  
            self.longest_path = our_igraph_data[self.project_name]["longest_path"]  
            self.max_path_length = our_igraph_data[self.project_name]["max_path_length"]  
            self.avg_path_length = our_igraph_data[self.project_name]["avg_path_length"]  
            self.avg_outdegree_of_neighbors = our_igraph_data[self.project_name]["avg_outdegree_of_neighbors"]  
            self.avg_pagerank_of_neighbors = our_igraph_data[self.project_name]["avg_pagerank_of_neighbors"]  
            self.higher_pagerank_neighborhood_size = our_igraph_data[self.project_name]["higher_pagerank_neighborhood_size"]  
            self.higher_pagerank_neighbors = our_igraph_data[self.project_name]["higher_pagerank_neighbors"]  
            self.academic_neighborhood_size = our_igraph_data[self.project_name]["academic_neighborhood_size"]  
            print "pagerank of {} is {}".format(self.project_name, self.pagerank)
        except KeyError:
            print "network params for {} were not calculated".format(self.project_name)
            self.pagerank = None
            self.neighborhood_size = None
            self.indegree = None
            self.eccentricity = None
            self.closeness = None            
            self.betweenness = None            
            self.eigenvector_centrality = None            
            self.longest_path = None            
            self.max_path_length = None            
            self.avg_path_length = None            
            self.avg_outdegree_of_neighbors = None            
            self.avg_pagerank_of_neighbors = None            
            self.higher_pagerank_neighborhood_size = None
            self.higher_pagerank_neighbors = None
            self.academic_neighborhood_size = None


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
            cls.num_citations,
            cls.impact
        )
        q = q.filter(cls.is_academic==True)
        rows = q.all()

        ref_list["num_downloads"] = sorted([row[0] for row in rows if row[0] != None])
        ref_list["pagerank"] = sorted([row[1] for row in rows if row[1] != None])
        ref_list["num_citations"] = sorted([row[2] for row in rows if row[2] != None])
        ref_list["impact"] = sorted([row[3] for row in rows if row[3] != None])

        return ref_list


    def _calc_percentile(self, refset, value):
        if value is None:  # distinguish between that and zero
            return None
         
        try:
            matching_index = refset.index(value)
            percentile = float(matching_index) / len(refset)
        except ValueError:
            # not in index.  maybe isn't academic.
            percentile = None
        return percentile

    def set_num_downloads_percentile(self, refset):
        self.num_downloads_percentile = self._calc_percentile(refset, self.num_downloads)

    def set_pagerank_percentile(self, refset):
        self.pagerank_percentile = self._calc_percentile(refset, self.pagerank)

    def set_num_citations_percentile(self, refset):
        self.num_citations_percentile = self._calc_percentile(refset, self.num_citations)

    def set_impact_percentile(self, refset):
        self.impact_percentile = self._calc_percentile(refset, self.impact)

    def set_all_percentiles(self, refsets_dict):
        self.set_num_downloads_percentile(refsets_dict["num_downloads"])
        self.set_pagerank_percentile(refsets_dict["pagerank"])
        self.set_num_citations_percentile(refsets_dict["num_citations"])
        self.set_impact_percentile(refsets_dict["impact"])


    @classmethod
    def _shortcut_rank(cls, name_to_rank_by):
        print "getting the lookup for ranking impact...."
        property_to_rank_by = getattr(cls, name_to_rank_by)

        q = db.session.query(cls.id)
        q = q.filter(cls.is_academic==True)
        q = q.order_by(property_to_rank_by.desc())  # the important part :)
        rows = q.all()

        impact_rank_lookup = {}
        ids_sorted = [row[0] for row in rows]
        for my_id in ids_sorted:
            zero_based_rank = ids_sorted.index(my_id)
            impact_rank_lookup[my_id] = zero_based_rank + 1

        return impact_rank_lookup

    @classmethod
    def shortcut_impact_rank(cls):
        return cls._shortcut_rank("impact")

    def set_impact_rank(self, impact_rank_lookup):
        try:
            self.impact_rank = impact_rank_lookup[self.id]
        except KeyError:
            # maybe isn't academic
            self.impact_rank = None
        print "self.impact_rank", self.impact_rank


    @property
    def display_num_downloads_score(self):
        return min(self.num_downloads_score, 1000)

    @property
    def display_num_citations_score(self):
        return min(self.num_citations_score, 1000)

    @property
    def display_pagerank_score(self):
        #if no pagerank, sub it for downloads
        if not self.pagerank_score:
            return self.num_downloads_score

        pagerank_score = self.pagerank_score
        if pagerank_score < 1:
            pagerank_score = 0
        return min(pagerank_score, 1000)





    @property
    def pagerank_offset_to_recenter_scores(self):
        use_min = self.pagerank_min        
        offset = -math.log10(use_min/self.pagerank_99th)
        return offset

    @property
    def pagerank_score_multiplier(self):
        return 1000.0/self.pagerank_offset_to_recenter_scores # makes it out of 1000

    @property
    def num_downloads_offset_to_recenter_scores(self):
        return -math.ceil(math.log10(1.0/self.num_downloads_99th))


    @property
    def num_downloads_score_multiplier(self):
        return 1000.0/self.num_downloads_offset_to_recenter_scores # makes it out of 1000

    @property
    def num_citations_offset_to_recenter_scores(self):
        use_min = 0.25
        ret = -math.log10(use_min/self.num_citations_99th)
        return ret

    @property
    def num_citations_score_multiplier(self):
        ret = 1000.0/self.num_citations_offset_to_recenter_scores  # makes it out of 1000
        return ret

    def set_pagerank_score(self):
        if not self.pagerank:
            self.pagerank_score = None
            return self.pagerank_score

        try:
            raw = math.log10(float(self.pagerank)/self.pagerank_99th)
            temp = (raw + self.pagerank_offset_to_recenter_scores)
            adjusted = temp * self.pagerank_score_multiplier
        except ValueError:
            adjusted = None

        self.pagerank_score = adjusted

        print u"\n**{}:  {} pagerank*10000, score {}\n".format(
            self.id, self.pagerank*10000, self.pagerank_score)        
        return self.pagerank_score


    def set_num_citations_score(self):
        if not self.num_citations:
            self.num_citations_score = 0
            print u"\n**{}:  {} num_citations, score {}\n".format(
                self.id, self.num_citations, self.num_citations_score)                    
            return self.num_citations_score

        try:
            raw = math.log10(float(self.num_citations)/self.num_citations_99th)
            temp = (raw + self.num_citations_offset_to_recenter_scores)
            adjusted = temp * self.num_citations_score_multiplier
        except ValueError:
            adjusted = None

        self.num_citations_score = adjusted
        print u"\n**{}:  {} num_citations, score {}\n".format(
            self.id, self.num_citations, self.num_citations_score)        
        return self.num_citations_score


    def set_num_downloads_score(self):
        if not self.num_downloads:
            self.num_downloads_score = None
            return self.num_downloads_score

        try:
            raw = math.log10(float(self.num_downloads)/self.num_downloads_99th)
            adjusted = (raw + self.num_downloads_offset_to_recenter_scores) * self.num_downloads_score_multiplier
        except ValueError:
            adjusted = None

        self.num_downloads_score = adjusted   
        print u"\n**{}:  {} downloads, score {}\n".format(
            self.id, self.num_downloads, self.num_downloads_score)        
        return self.num_downloads_score







    def set_impact(self):
        if not self.is_academic:
            self.impact = None
            print u"self.impact for {} is None because isn't academic"
            return 

        use_for_pagerank = self.pagerank_percentile
        if not use_for_pagerank:
            use_for_pagerank = self.num_downloads_percentile
        combo = (use_for_pagerank + self.num_downloads_percentile + self.num_citations_percentile) / 3.0
        self.impact = combo
        # print u"self.impact for {} is {} ({}, {}, {}".format(
        #     self.id, 
        #     self.impact, 
        #     self.pagerank_score, self.num_downloads_score, self.num_citations_score)



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
        return namespace + ":" + name

    elif namespace == "python":
        return "pypi:" + name

    elif namespace == "r":
        return "cran:" + name

    else:
        raise ValueError("Invalid namespace for package id")


def make_host_name(host_or_language):
    if host_or_language=="python":
        return "pypi"
    elif host_or_language=="r":
        return "cran"
    elif host_or_language in ["cran", "pypi"]:
        return host_or_language
    else:
        raise ValueError("You're not passing in a valid host or language name.")

def make_language(host_or_language):
    if host_or_language=="pypi":
        return "python"
    elif host_or_language=="cran":
        return "r"
    elif host_or_language in ["python", "r"]:
        return host_or_language
    else:
        raise ValueError("You're not passing in a valid host or language name.")







def shortcut_igraph_data_dict():

    print "loading is_academic"
    # todo: need to make this specific to the host
    rows = db.session.query(Package.project_name).filter(Package.is_academic==True).all()
    academic_package_names = [row[0] for row in rows]
    print "first few academic_package_names:", academic_package_names[0:10]

    print "loading text dataset into igraph"
    our_graph = igraph.read("dep_nodes_ncol.txt", format="ncol", directed=True, names=True)

    print "loaded, now calculating..."
    our_vertice_names = our_graph.vs()["name"]
    our_pageranks = our_graph.pagerank(implementation="prpack")
    our_neighborhood_size = our_graph.neighborhood_size(our_graph.vs(), mode="IN", order=100)
    our_indegree = our_graph.vs().indegree()
    our_outdegree = our_graph.vs().outdegree()
    our_eccentricities = our_graph.eccentricity(mode="IN")
    our_closeness = our_graph.closeness(mode="IN")
    our_betweenness = our_graph.betweenness()
    our_eigenvector_centrality = our_graph.eigenvector_centrality(directed=False)

    our_longest_paths = defaultdict(str)
    our_max_path_lengths = defaultdict(int)
    our_avg_path_lengths = defaultdict(int)
    our_outdegree_of_neighbors = defaultdict(int)
    our_pagerank_of_neighbors = defaultdict(int)
    our_higher_pagerank_neighborhood_size = defaultdict(int)
    our_higher_pagerank_neighbors = defaultdict(list)
    our_academic_neighborhood_size = defaultdict(int)

    for v in our_graph.vs():
        name = v["name"]
        if v["name"].startswith("github"):
            continue
        print v["name"]
        paths = our_graph.get_all_shortest_paths(v, mode="IN")
        longest_path_indices = sorted(paths, key=len, reverse=True)[0]
        longest_path_names = our_graph.vs()[longest_path_indices]["name"]
        our_longest_paths[name] = longest_path_names

        list_of_lengths = [len(p) for p in paths]
        our_max_path_lengths[name] = max(list_of_lengths)
        our_avg_path_lengths[name] = float(sum(list_of_lengths))/len(list_of_lengths)

        sum_outdegree_of_neighbors = 0
        sum_pagerank_of_neighbors = 0
        first_order_neighbours = our_graph.neighbors(v, mode="IN")
        if first_order_neighbours:
            for neighbor_index in first_order_neighbours:
                sum_outdegree_of_neighbors += our_outdegree[neighbor_index]
                sum_pagerank_of_neighbors += our_pageranks[neighbor_index]
            our_outdegree_of_neighbors[name] = sum_outdegree_of_neighbors / len(first_order_neighbours)
            our_pagerank_of_neighbors[name] = sum_pagerank_of_neighbors / len(first_order_neighbours)
        else:
            our_outdegree_of_neighbors[name] = None
            our_pagerank_of_neighbors[name] = None

        neighborhood = our_graph.neighborhood(v, mode="IN")
        if neighborhood:
            for neighbor_index in neighborhood:
                if neighbor_index == v.index:
                    # this is us.  skip.
                    continue

                if our_pageranks[neighbor_index] >= our_pageranks[v.index]:
                    our_higher_pagerank_neighborhood_size[name] += 1
                    our_higher_pagerank_neighbors[name].append(neighbor_package_name)

                neighbor_package_name = our_vertice_names[neighbor_index]
                if neighbor_package_name in academic_package_names:
                    our_academic_neighborhood_size[name] += 1


    print "reformating data into dict ..."
    global our_igraph_data
    our_igraph_data = {}
    for (i, name) in enumerate(our_vertice_names):
        our_igraph_data[name] = {
            "pagerank": our_pageranks[i],
            "neighborhood_size": our_neighborhood_size[i],
            "indegree": our_indegree[i],
            "eccentricity": our_eccentricities[i],
            "closeness": our_closeness[i],
            "betweenness": our_betweenness[i],
            "eigenvector_centrality": our_eigenvector_centrality[i],
            "longest_path": our_longest_paths[name],  #was stored in a dict
            "max_path_length": our_max_path_lengths[name], #was stored in a dict
            "avg_path_length": our_avg_path_lengths[name],  #was stored in a dict
            "avg_outdegree_of_neighbors": our_outdegree_of_neighbors[name],  #was stored in a dict
            "avg_pagerank_of_neighbors": our_pagerank_of_neighbors[name],  #was stored in a dict
            "higher_pagerank_neighbors": our_higher_pagerank_neighbors[name],  #was stored in a dict
            "higher_pagerank_neighborhood_size": our_higher_pagerank_neighborhood_size[name],  #was stored in a dict
            "academic_neighborhood_size": our_academic_neighborhood_size[name]  #was stored in a dict
        }

    return our_igraph_data


















