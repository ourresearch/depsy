from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import func
from sqlalchemy import sql
from time import time
import json
from validate_email import validate_email
from distutils.version import StrictVersion
import zipfile
import requests
import hashlib
from lxml import html
import numpy
import os

from models import github_api
from models.person import Person
from models.person import get_or_make_person
from models.contribution import Contribution
from models.github_repo import GithubRepo
from models.zip_getter import ZipGetter
from models.pypi_project import pypi_package_names
from jobs import enqueue_jobs
from jobs import update_registry
from jobs import Update
from util import elapsed
from util import dict_from_dir
from util import truncate
from python import parse_requirements_txt





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
    summary = db.Column(db.Text)

    sort_score = db.Column(db.Float)

    num_committers = db.Column(db.Integer)
    num_commits = db.Column(db.Integer)
    num_authors = db.Column(db.Integer)

    inactive = db.Column(db.Text)


    contributions = db.relationship(
        'Contribution',
        lazy='immediate',
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
        ret = dict_from_dir(self, keys_to_ignore=[
            "proxy_papers",
            "github_contributors",
            "bucket",
            "requires_files",
            "contributions",
            "api_raw",
            "setup_py",
            "person",
            "downloads"
        ])
        if full:
            ret["contributions"] = [c.to_dict() for c in self.contributions]

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

            "num_depended_on": self.num_depended_on,
            "num_depended_on_percentile": self.num_depended_on_percentile,

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

    def save_github_owner_to_db(self):
        if not self.github_owner:
            return False

        person = get_or_make_person(github_login=self.github_owner)
        self._save_contribution(person,  "github_owner")


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

        self.pmc_mentions = pmc_mentions
        return self.pmc_mentions

    def set_use(self):
        try:
            num_depended_on = g.vs.find(self.project_name).strength(mode="OUT", weights="weight")
            print "num_depended_on for {} is {}".format(self.project_name, num_depended_on)
        except ValueError:
            num_depended_on = 0
            print "no num_depended_on found for {}".format(self.project_name)
        self.num_depended_on = num_depended_on

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
    def _group_by_host(cls, rows):
        ret = {
            "pypi": sorted([row[1] for row in rows if row[0]=="pypi" and row[1]!=None]),
            "cran": sorted([row[1] for row in rows if row[0]=="cran" and row[1]!=None])
        }

        return ret

    @classmethod
    def get_downloads_by_host(cls):
        q = db.session.query(cls.host, cls.num_downloads)
        q = q.filter(Package.inactive == None)
        rows = q.all()
        return cls._group_by_host(rows)

    @classmethod
    def get_uses_by_host(cls):
        q = db.session.query(cls.host, cls.num_depended_on)
        q = q.filter(Package.inactive == None)
        rows = q.all()
        return cls._group_by_host(rows)

    @classmethod
    def get_stars_by_host(cls):
        q = db.session.query(cls.host, cls.num_stars)
        q = q.filter(Package.inactive == None)
        rows = q.all()
        return cls._group_by_host(rows)

    @classmethod
    def get_num_citations_by_host(cls):
        q = db.session.query(cls.host, cls.num_citations)
        q = q.filter(Package.inactive == None)
        rows = q.all()
        return cls._group_by_host(rows)

    def _calc_percentile(self, refset, value):
        if value == None:  # distinguish between that and zero
            return None

        percentiles = [i/10000.0 for i in range(0, 100*10000)]
        percentile_cutoffs = numpy.percentile(refset[self.host], percentiles)
        percentile_lookup = zip(percentile_cutoffs, percentiles)
        for (cutoff, percentile) in zip(percentile_cutoffs, percentiles):
            if cutoff >= value:
                return percentile
        return 99.99

    def set_num_downloads_percentile(self):
        global num_downloads_refset
        self.num_downloads_percentile = self._calc_percentile(num_downloads_refset, self.num_downloads)

    def set_num_depended_on_percentile(self):
        global num_depended_on_refset
        self.num_depended_on_percentile = self._calc_percentile(num_depended_on_refset, self.num_depended_on)

    def set_num_star_percentile(self):
        global num_stars_refset
        self.num_stars_percentile = self._calc_percentile(num_stars_refset, self.num_stars)

    def set_num_citations_percentile(self):
        global num_citations_refset
        self.num_citations_percentile = self._calc_percentile(num_citations_refset, self.num_citations)

    def set_all_percentiles(self):
        self.set_num_downloads_percentile()
        self.set_num_depended_on_percentile()
        self.set_num_star_percentile()
        self.set_num_citations_percentile()
        self.set_sort_score()


class PypiPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'pypi'
    }

    def __repr__(self):
        return u'<PypiPackage {name}>'.format(
            name=self.id)

    @property
    def source_url(self):
        if not self.api_raw:
            return None

        if "releases" in self.api_raw and self.api_raw["releases"]:
            versions = self.api_raw["releases"].keys()

            try:
                versions.sort(key=StrictVersion, reverse=True)
            except ValueError:
                versions #give up sorting, just go for it

            for version in versions:
                release_dict = self.api_raw["releases"][version]
                for url_dict in release_dict:
                    if "packagetype" in url_dict:

                        # trying these in priority order
                        valid_type = ["bdist_wheel", "bdist_egg", "sdist", "bdist_dumb"]
                        for packagetype in valid_type:
                            if url_dict["packagetype"]==packagetype:
                                if "url" in url_dict and url_dict["url"].startswith("http"):
                                    return url_dict["url"]

            if "download_url" in self.api_raw["info"] and self.api_raw["info"]["download_url"]:
                if self.api_raw["info"]["download_url"].startswith("http"):
                    return self.api_raw["info"]["download_url"]

        return None


    def save_host_contributors(self):
        author = self.api_raw["info"]["author"]
        author_email = self.api_raw["info"]["author_email"]

        if not author:
            return False

        if author_email and validate_email(author_email):
            person = get_or_make_person(name=author, email=author_email)
        else:
            person = get_or_make_person(name=author)

        self._save_contribution(person, "author")


    def set_github_repo_ids(self):
        q = db.session.query(GithubRepo.login, GithubRepo.repo_name)
        q = q.filter(GithubRepo.bucket.contains({"setup_py_name": self.project_name}))
        q = q.order_by(GithubRepo.api_raw['stargazers_count'].cast(db.Integer).desc())

        start = time()
        row = q.first()
        print "Github repo query took {}".format(elapsed(start, 4))

        if row is None:
            return None

        else:
            print "Setting a new github repo for {}: {}/{}".format(
                self,
                row[0],
                row[1]
            )
            self.github_owner = row[0]
            self.github_repo_name = row[1]
            self.bucket["matched_from_github_metadata"] = True


    def _get_files(self, filenames_to_get):

        print "getting requires files for {} from {}".format(
            self.id, self.source_url)
        if not self.source_url:
            print "No source_url, so skipping"
            return {"error": "error_no_source_url"}

        getter = ZipGetter(self.source_url)

        ret = getter.download_and_extract_files(filenames_to_get)

        if getter.error:
            print "Problems with the downloaded zip, quitting without getting filenames."
            ret = {"error": "error_with_zip"}

        return ret


    def set_requires_files(self):
        # from https://pythonhosted.org/setuptools/formats.html#dependency-metadata
        filenames_to_get = [
            "/requires.txt",
            "/metadata.json",
            "/METADATA"
        ]
        self.requires_files = self._get_files(filenames_to_get)
        return self.requires_files

    def set_setup_py(self):
        res = self._get_files(["setup.py"])
        if "error" in res:
            self.setup_py = res["error"]  # save the error string

        else:
            try:
                self.setup_py = res["setup.py"]

                # major hack! comment this in ONLY when there's nothing
                # left to check but weird files that break on UTF-8 errors.
                #self.setup_py = "error_utf8"

                self.setup_py_hash = hashlib.md5(res["setup.py"]).hexdigest()

            except KeyError:
                # seems there is in setup.py here.
                self.setup_py = "error_not_found"

        return self.setup_py



    def set_api_raw(self):
        requests.packages.urllib3.disable_warnings()
        url = 'https://pypi.python.org/pypi/{}/json'.format(self.project_name)
        r = requests.get(url)
        try:
            self.api_raw = r.json()
        except ValueError:
            self.api_raw = {"error": "no_json"}


    def set_host_reverse_deps(self):
        core_requirement_lines = ""

        if "METADATA" in self.requires_files:
            requirement_text = self.requires_files["METADATA"]
            # exclude everything after a heading
            core_requirement_list = []
            for line in requirement_text.split("\n"):

                # see spec at https://www.python.org/dev/peps/pep-0345/#download-url
                # "Requires" start is depricated
                if line.startswith("Requires-Dist:") or line.startswith("Requires:"):
                    line = line.replace("Requires-Dist:", "")
                    line = line.replace("Requires:", "")
                    if ";" in line:
                        # has extras in it... so isn't in core requirements, so skip
                        pass
                    else:
                        core_requirement_list += [line]
            core_requirement_lines = "\n".join(core_requirement_list)

        elif "requires.txt" in self.requires_files:
            requirement_text = self.requires_files["requires.txt"]

            # exclude everything after a heading
            core_requirement_list = []
            for line in requirement_text.split("\n"):
                if line.startswith("["):
                    break
                core_requirement_list += [line]
            core_requirement_lines = "\n".join(core_requirement_list)

        reverse_deps = parse_requirements_txt(core_requirement_lines)

        print "found requirements={}\n\n".format(reverse_deps)
        if not reverse_deps:
            self.host_reverse_deps = []
            return None

        # see if is in pypi, case insensitively, getting normalized case
        reverse_deps_in_pypi = []
        for dep in reverse_deps:
            if dep.lower() in pypi_package_names:
                pypi_package_normalized_case = pypi_package_names[dep.lower()]
                reverse_deps_in_pypi.append(pypi_package_normalized_case)

        if len(reverse_deps_in_pypi) != len(reverse_deps):
            print "some reverse deps not in pypi for {}:{}".format(
                self.id, set(reverse_deps) - set(reverse_deps_in_pypi))
            print reverse_deps
            print reverse_deps_in_pypi
        self.host_reverse_deps = reverse_deps_in_pypi


    def set_tags(self):
        self.tags = []
        tags_to_reject = [
            "Python Modules",
            "Libraries",
            "Software Development"
        ]
        try:
            pypi_classifiers = self.api_raw["info"]["classifiers"]
        except KeyError:
            print "no keywords for {}".format(self)
            return None

        working_tag_list = []
        for classifier in pypi_classifiers:
            if not classifier.startswith("Topic"):
                continue

            # the first 'tag' is useless
            my_tags = classifier.split(" :: ")[1:]
            working_tag_list += my_tags

        unique_tags = list(set(working_tag_list))
        for tag in unique_tags:
            if len(tag) > 1 and tag not in tags_to_reject:
                self.tags.append(tag)

        if len(self.tags):
            print "set tags for {}: {}".format(self, ",".join(self.tags))
        else:
            print "found no tags for {}".format(self)

        return self.tags


    @property
    def as_snippet(self):
        ret = self._as_package_snippet
        ret["language"] = "python"
        return ret



class CranPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'cran'
    }

    def __repr__(self):
        return u'<CranPackage {name}>'.format(
            name=self.id)

    def _return_clean_author_string(self, all_authors):
        halt_patterns = ["punt", "adapted", "comply"]
        for pattern in halt_patterns:
            if pattern in all_authors:
                return None

        remove_patterns = [
            "\(.*\)",
            "\[.*\]",
            "with.*$",
            "assistance.*$",
            "contributions.*$",
            "under.*$",
            "and others.*$",
            "and many others.*$",
            "and authors.*$",
            "assisted.*$",
            "\..*$",
        ]
        for pattern in all_patterns:
            all_authors = re.sub(pattern, "", all_authors)
        all_authors = all_authors.replace("<U+000a>", " ")
        all_authors = all_authors.replace("\n", " ")
        all_authors = all_authors.replace("&", ",")
        all_authors = all_authors.replace("and", ",")
        return all_authors

    def save_host_contributors(self):
        all_authors = self.api_raw["Author"]
        maintainer = self.api_raw["Maintainer"]

        clean_author_string = self._return_clean_author_string(all_authors)
        author_parts = clean_author_string.split(",")
        for part in author_parts:
            match = re.findall("(.*)(\<.*\>)?", part)
            # if match and len(match)
            #     name = match[0]
            #     email = match[1]

        #if not author:
        #    return False
        #
        #if author_email and validate_email(author_email):
        #    person = get_or_make_person(name=author, email=author_email)
        #else:
        #    person = get_or_make_person(name=author)
        #
        #self._save_contribution(person, "author")






    def _remove_all_authors_cruft(self, all_authors):
        return all_authors

    def _extract_author_strings(self, all_authors):
        return []

    def _name_and_email_from_author_str(self, author_str):
        return [None, None]


    def set_github_repo_ids(self):
        q = db.session.query(GithubRepo.login, GithubRepo.repo_name)
        q = q.filter(GithubRepo.language == 'r')
        q = q.filter(GithubRepo.login != 'cran')  # these are just mirrors.
        q = q.filter(GithubRepo.bucket.contains({"cran_descr_file_name": self.project_name}))
        q = q.order_by(GithubRepo.api_raw['stargazers_count'].cast(db.Integer).desc())

        start = time()
        row = q.first()
        print "Github repo query took {}".format(elapsed(start, 4))

        if row is None:
            return None

        else:
            print "Setting a new github repo for {}: {}/{}".format(
                self,
                row[0],
                row[1]
            )
            self.github_owner = row[0]
            self.github_repo_name = row[1]
            self.bucket["matched_from_github_metadata"] = True


    def set_num_downloads_since(self):

        ### hacky!  hard code this
        get_downloads_since_date = "2015-07-25"

        if not self.num_downloads:
            return None

        download_sum = 0

        for download_dict in self.downloads.get("daily_downloads", []):
            if download_dict["day"] > get_downloads_since_date:
                download_sum += download_dict["downloads"]

        self.downloads["last_month"] = download_sum

    @property
    def as_snippet(self):
        ret = self._as_package_snippet
        ret["host"] = "r"
        return ret


    def set_host_reverse_deps(self):
        self.host_reverse_deps = []
        for dep_kind in ["reverse_depends", "reverse_imports"]:
            if dep_kind in self.all_r_reverse_deps:
                self.host_reverse_deps += self.all_r_reverse_deps[dep_kind]



def prep_summary(str):
    placeholder = "A nifty project."
    if not str:
        return placeholder
    elif str == "UNKNOWN":
        return placeholder
    else:
        return truncate(str)



def get_packages(sort="sort_score", filters=None):
    allowed_sorts = [
        "sort_score",
        "citations"
    ]


    q = db.session.query(Package)

    q = q.limit(100)

    ret = q.all()
    return ret






def save_host_contributors_pypi(limit=10):
    # has to be run all in one go, db stores no indicator this has run.
    q = db.session.query(PypiPackage.id)
    q = q.order_by(Package.project_name)
    q = q.limit(limit)

    update_fn = make_update_fn(Package, "save_host_contributors")
    for row in q.all():
        update_fn(row[0])


def save_host_contributors_cran(limit=10):
    # has to be run all in one go, db stores no indicator this has run.
    q = db.session.query(CranPackage.id)
    q = q.order_by(Package.project_name)
    q = q.limit(limit)

    update_fn = make_update_fn(Package, "save_host_contributors")
    for row in q.all():
        update_fn(row[0])


def set_all_github_contributors(limit=10, use_rq="rq"):
    q = db.session.query(Package.id)
    q = q.filter(Package.github_repo_name != None)
    q = q.filter(Package.github_contributors == None)
    q = q.order_by(Package.project_name)
    q = q.limit(limit)

    enqueue_jobs(Package, "set_github_contributors", q, 1, use_rq)







def set_all_pypi_github_repo_ids(limit=10, use_rq="rq", chunk_size=1000):

    q = db.session.query(PypiPackage.id)
    q = q.filter(PypiPackage.github_repo_name == None)
    q = q.order_by(PypiPackage.project_name)
    q = q.limit(limit)

    enqueue_jobs(PypiPackage, "set_github_repo_ids", q, 1, use_rq, chunk_size)





def set_all_cran_github_repo_ids(limit=10, use_rq="rq", chunk_size=1000):

    q = db.session.query(CranPackage.id)
    q = q.filter(CranPackage.github_repo_name == None)
    q = q.order_by(CranPackage.project_name)
    q = q.limit(limit)

    enqueue_jobs(CranPackage, "set_github_repo_ids", q, 1, use_rq, chunk_size)





def make_persons_from_github_owner_and_contribs(limit=10, use_rq="rq"):
    q = db.session.query(Package.id)
    q = q.filter(Package.github_repo_name != None)
    q = q.filter(Package.bucket.contains({"matched_from_github_metadata": True}))
    q = q.order_by(Package.id)
    q = q.limit(limit)

    enqueue_jobs(Package, "save_github_owners_and_contributors", q, 1, use_rq)


def test_me(limit=10, use_rq="rq"):
    q = db.session.query(Package.id)
    q = q.order_by(Package.id)
    q = q.limit(limit)

    # doesn't matter what this is now, because update function overwritten
    enqueue_jobs(Package, "set_github_repo_ids", q, 6, use_rq)




######## igraph
g = None

q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.num_depended_on == None)

update_registry.register(Update(
    job=PypiPackage.set_use,
    query=q,
    queue_id=5
))


def run_igraph(limit=2):
    import igraph
    global g

    print "loading in igraph"
    g = igraph.read("dep_nodes_ncol.txt", format="ncol", directed=True, names=True)
    print "loaded, now getting uses"
    # g.vs.find("Django").strength(mode="OUT", weights="weight")

    update = update_registry.get("PypiPackage.set_use")
    update.run(
        no_rq=True,
        obj_id=None,
        num_jobs=limit,
        chunk_size=100
    )



############

# # update everything
# python update.py PypiPackage.set_requires_files --limit 10 --chunk 5 --no-rq

# # update one thing
# python update.py PypiPackage.set_requires_files --id pypi:fastly --no-rq


q = db.session.query(PypiPackage.id)
q = q.filter(PypiPackage.requires_files != None)

update_registry.register(Update(
    job=PypiPackage.set_host_reverse_deps,
    query=q,
    queue_id=5
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
q = q.filter(PypiPackage.tags == None)

update_registry.register(Update(
    job=PypiPackage.set_tags,
    query=q,
    queue_id=2
))


# for all Packages, not just pypi
q = db.session.query(Package.id)
q = q.filter(Package.sort_score == None)

update_registry.register(Update(
    job=Package.set_sort_score,
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
    num_downloads_refset = Package.get_downloads_by_host()
    num_depended_on_refset = Package.get_uses_by_host()
    num_stars_refset = Package.get_stars_by_host()
    num_citations_refset = Package.get_num_citations_by_host()
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
q = q.filter(Package.inactive == None)
update_registry.register(Update(
    job=Package.set_all_percentiles,
    query=q,
    queue_id=8
))


q = db.session.query(CranPackage.id)
update_registry.register(Update(
    job=CranPackage.set_host_reverse_deps,
    query=q,
    queue_id=8
))


# q = db.session.query(Package.id)
# q = q.filter(Package.num_depended_on != None)
# q = q.filter(Package.num_depended_on_percentile == None)
# update_registry.register(Update(
#     job=Package.set_num_depended_on_percentile,
#     query=q,
#     queue_id=8
# ))

# q = db.session.query(Package.id)
# q = q.filter(Package.num_stars != None)
# q = q.filter(Package.num_stars_percentile == None)
# update_registry.register(Update(
#     job=Package.set_stars_percentile,
#     query=q,
#     queue_id=8
# ))

# q = db.session.query(Package.id)
# q = q.filter(Package.num_citations != None)
# q = q.filter(Package.num_citations_percentile == None)
# update_registry.register(Update(
#     job=Package.set_num_citations_percentile,
#     query=q,
#     queue_id=8
# ))











