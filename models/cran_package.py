from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import sql

from time import time
from validate_email import validate_email
import re
from jobs import update_registry
from jobs import Update

from models.person import get_or_make_person
from models.package import Package
from models.github_repo import GithubRepo
from util import elapsed
from collections import defaultdict

class CranPackage(Package):
    __mapper_args__ = {
        'polymorphic_identity': 'cran'
    }

    def __repr__(self):
        return u'<CranPackage {name}>'.format(
            name=self.id)

    def _return_clean_author_string(self, all_authors):
        # print "all authors before:", all_authors

        halt_patterns = [" punt ", " adapted ", " comply "]
        for pattern in halt_patterns:
            if pattern in all_authors:
                return None

        remove_patterns = [
            "\(.*?\)",
            "\[.*?\]",
            "with.*$",
            "assistance.*$",
            "contributions.*$",
            "under.*$",
            "and others.*$",
            "and many others.*$",
            "and authors.*$",
            "assisted.*$"
        ]
        for pattern in remove_patterns:
            all_authors = re.sub(pattern, "", all_authors)
            # print pattern, all_authors

        all_authors = all_authors.replace("<U+000a>", " ")
        all_authors = all_authors.replace("\n", " ")
        all_authors = all_authors.replace(" & ", ",")
        all_authors = all_authors.replace(" and ", ",")
        all_authors.strip(" .")
        # print "all authors after:", all_authors
        return all_authors

    @property
    def language(self):
        return "r"

    def save_host_contributors(self):
        all_authors = self.api_raw["Author"]
        maintainer = self.api_raw["Maintainer"]

        print "starting with all_authors", all_authors
        clean_author_string = self._return_clean_author_string(all_authors)
        if not clean_author_string:
            return None

        author_parts = clean_author_string.split(",")
        author_name = None
        author_email = None
        for clean_part in author_parts:
            # print "clean_part", clean_part
            if "<" in clean_part:
                match = re.search(ur"(.*)(?:\w*\<(.*)\>)", clean_part)
                if match:
                    author_name = match.group(0)
                    author_email = match.group(1)
                else:
                    print u"no email match on", clean_part
            else:
                author_name = clean_part

            if author_name:
                author_name = author_name.strip()
                if author_email and validate_email(author_email):
                   person = get_or_make_person(name=author_name, email=author_email)
                else:
                   person = get_or_make_person(name=author_name)
                print u"saving person {}".format(person)
                self._save_contribution(person, "author")






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



    def set_host_reverse_deps(self):
        self.host_reverse_deps = []
        for dep_kind in ["reverse_depends", "reverse_imports"]:
            if dep_kind in self.all_r_reverse_deps:
                self.host_reverse_deps += self.all_r_reverse_deps[dep_kind]




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












########################################################################

# shortcut functions

########################################################################

def shortcut_rev_deps_pairs():

    command = """select package, 
                    used_by, 
                    pagerank, 
                    (COALESCE((github_repo.api_raw->>'stargazers_count')::int, 0) 
                        + COALESCE(package.num_stars, 0)) as num_stars
                from dep_nodes_ncol_cran_reverse
                left outer join github_repo 
                    on dep_nodes_ncol_cran_reverse.used_by = 'github:' || github_repo.id
                left outer join package 
                    on dep_nodes_ncol_cran_reverse.used_by = package.project_name"""

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











########################################################################

# update functions

########################################################################



q = db.session.query(CranPackage.id)
update_registry.register(Update(
    job=CranPackage.set_rev_deps_tree,
    query=q,
    shortcut_fn=shortcut_rev_deps_pairs
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













