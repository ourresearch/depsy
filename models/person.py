import hashlib
from collections import defaultdict
from time import sleep

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import or_
from nameparser import HumanName

from app import db
from models.contribution import Contribution
from models.github_api import GithubRateLimitException
from github_api import get_profile
from util import dict_from_dir

# reused elsewhere
def add_person_leaderboard_filters(q):
    q = q.filter(or_(Person.name == None, Person.name != "UNKNOWN"))
    q = q.filter(or_(Person.email == None, Person.email != "UNKNOWN"))
    q = q.filter(Person.is_organization == False)
    return q

class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text)
    name = db.Column(db.Text)
    other_names = db.Column(JSONB)
    github_login = db.Column(db.Text)
    github_about = db.deferred(db.Column(JSONB))
    bucket = db.Column(JSONB)
    impact = db.Column(db.Float)
    impact_rank = db.Column(db.Integer)
    parsed_name = db.Column(JSONB)
    is_academic = db.Column(db.Boolean)
    is_organization = db.Column(db.Boolean)
    main_language = db.Column(db.Text)

    type = db.Column(db.Text)


    def __repr__(self):
        return u'<Person "{name}" ({id})>'.format(
            name=self.name,
            id=self.id
        )

    contributions = db.relationship(
        'Contribution',
        # lazy='select',
        cascade="all, delete-orphan",
        backref="person"
    )


    def set_is_academic(self):
        # set this using the sql in the sql folder!  set_person_is_academic.sql
        # this is just a placeholder to remind us to run it :)
        pass

    def set_is_organization(self):
        # set this using the sql in the sql folder!  set_person_is_organization.sql
        # this is just a placeholder to remind us to run it :)
        pass

    def to_dict(self, max_person_packages=None, include_top_collabs=True):
        ret = self.as_package_snippet

        person_packages = self.get_person_packages()
        ret["num_packages"] = len(person_packages)
        ret["num_packages_r"] = len([pp for pp in person_packages if pp.package.language=='r'])
        ret["num_packages_python"] = len([pp for pp in person_packages if pp.package.language=='python'])
        
        # tags
        tags_dict = defaultdict(int)
        for pp in person_packages:
            for tag in pp.package.tags:
                tags_dict[tag] += 1
        tags_to_return = min(3, len(tags_dict))
        sorted_tags_to_return = sorted(tags_dict.items(), key=lambda x: x[1], reverse=True)[0:tags_to_return]
        ret["top_person_tags"] = [{"name": name, "count": count} for name, count in sorted_tags_to_return]

        # co-collaborators
        if include_top_collabs:
            my_collabs = defaultdict(float)
            for pp in person_packages:
                for collab_person_id, collab_credit in pp.package.credit.iteritems():
                    if collab_person_id != self.id:  #don't measure my own collab strength
                        collab_strength = collab_credit * pp.person_project_credit
                        my_collabs[collab_person_id] += collab_strength
            sorted_collabs_to_return = sorted(my_collabs.items(), key=lambda x: x[1], reverse=True)
            ret["top_collabs"] = []    
            num_collabs_to_return = min(5, len(sorted_collabs_to_return))    
            for person_id, collab_score in sorted_collabs_to_return[0:num_collabs_to_return]:
                person = Person.query.get(int(person_id))
                person_dict = person.as_package_snippet
                person_dict["collab_score"] = collab_score * 4  # to make a 0.25*0.25 connection strength of 1
                ret["top_collabs"].append(person_dict)

        # person packages
        if max_person_packages:
            person_packages_to_return = min(max_person_packages, len(person_packages))
            ret["person_packages"] = [p.as_person_snippet for p in person_packages[0:person_packages_to_return]]
        else:
            ret["person_packages"] = [p.to_dict() for p in person_packages]

        return ret


    @property
    def as_snippet(self):
        return self.to_dict(max_person_packages=3, include_top_collabs=False)

    @property
    def as_package_snippet(self):
        ret = {
            "id": self.id, 
            "name": self.display_name,
            "single_name": self.single_name,              
            "github_login": self.github_login, 
            "icon": self.icon, 
            "icon_small": self.icon_small, 
            "is_academic": self.is_academic, 
            "is_organization": self.is_organization,             
            "main_language": self.main_language,             
            "impact": self.impact, 
            "impact_rank": self.impact_rank, 
            "impact_rank_max": self.impact_rank_max, 
            "id": self.id
        }
        return ret


    def set_main_language(self):
        person_package_summary_dict = self.as_snippet
        if person_package_summary_dict["num_packages_r"] > person_package_summary_dict["num_packages_python"]:
            self.main_language = "r"
        else:
            self.main_language = "python"

    @classmethod
    def shortcut_impact_rank(cls):
        print "getting the lookup for ranking impact...."
        impact_rank_lookup = defaultdict(dict)
        for main_language in ["python", "r"]:
            q = db.session.query(cls.id)
            q = add_person_leaderboard_filters(q)
            q = q.filter(Person.main_language==main_language)
            q = q.order_by(cls.impact.desc())  # the important part :)
            rows = q.all()

            ids_sorted_by_impact = [row[0] for row in rows]
            for my_id in ids_sorted_by_impact:
                zero_based_rank = ids_sorted_by_impact.index(my_id)
                impact_rank_lookup[main_language][my_id] = zero_based_rank + 1

        return impact_rank_lookup


    def set_impact_rank(self, impact_rank_lookup):

        try:
            self.impact_rank = impact_rank_lookup[self.main_language][self.id]
        except KeyError:  # maybe because organization, or name=="UNKNOWN"
            print "couldn't find my id"
            self.impact_rank = None
        print "self.impact_rank", self.impact_rank

    @property
    def impact_rank_max(self):
        # select count(id), main_language 
        # from person 
        # where is_organization=false
        # and (name is null or name!='UKNOWN')
        # and (email is null or email!='UNKNOWN')
        # group by main_language

        if self.main_language == "python":
            return 62951
        elif self.main_language == "r":
            return 10447

    def set_github_about(self):
        if self.github_login is None:
            return None

        self.github_about = get_profile(self.github_login)
        try:
            if not self.name:
                self.name = self.github_about["name"]

            if not self.email :
                self.email = self.github_about["email"]
        except KeyError:

            # our github_about is an error object,
            # it's got no info about the person in it.
            return False



    def set_impact(self):
        self.impact = sum([pp.person_project_impact for pp in self.get_person_packages()])
        return self.impact

    def set_parsed_name(self):
        if not self.name:
            self.parsed_name = None
            return

        name = HumanName(self.name)
        self.parsed_name = name.as_dict()

    def _make_gravatar_url(self, size):
        try:
            if self.email is not None:
                hash = hashlib.md5(self.email).hexdigest()
            else:
                hash = hashlib.md5("placeholder@example.com").hexdigest()
        except UnicodeEncodeError:
            print "UnicodeEncodeError making gravatar url from email"
            hash = 42

        url = "http://www.gravatar.com/avatar/{hash}.jpg?s={size}&d=mm".format(
            hash=hash,
            size=size
        )
        return url

    @property
    def icon(self):
        return self._make_gravatar_url(160)

    @property
    def icon_small(self):
        return self._make_gravatar_url(30)

    def has_role_on_project(self, role, package_id):
        for c in self.contributions:
            if c.role == role and c.package_id == package_id:
                return True
        return False

    def num_commits_on_project(self, package_id):
        for c in self.contributions:
            if c.role == "github_contributor" and c.package_id == package_id:
                return c.quantity
        return False

    @property
    def single_name(self):
        if self.is_organization:
            return self.display_name
        elif self.parsed_name and self.parsed_name["last"]:
            return self.parsed_name["last"]
        return self.display_name

    @property
    def display_name(self):
        if self.name:
            return self.name
        elif self.github_login:
            return self.github_login
        elif self.email:
            return self.email.split("@")[0]
        else:
            return "name unknown"

    # could be a property, but kinda slow, so better as explicity method methinks
    def get_person_packages(self):
        person_packages = defaultdict(PersonPackage)
        for contrib in self.contributions:
            person_packages[contrib.package.id].set_role(contrib)

        person_packages_list = person_packages.values()
        person_packages_list.sort(key=lambda x: x.person_project_impact, reverse=True)
        return person_packages_list

    def num_commits_on_project(self, package_id):
        for c in self.contributions:
            if c.role == "github_contributor" and c.package_id == package_id:
                return c.quantity
        return False




class PersonPackage():
    def __init__(self):
        self.package = None
        self.person = None
        self.person_project_commits = None
        self.roles = []

    def set_role(self, contrib):
        if not self.package:
            self.package = contrib.package
        if not self.person:
            self.person = contrib.person
        if contrib.role == "github_contributor":
            self.person_project_commits = contrib.quantity
        self.roles.append(contrib)

    @property
    def person_project_credit(self):
        return self.package.get_credit_for_person(self.person.id)

    @property
    def person_project_impact(self):
        person_project_impact = self.person_project_credit * self.package.impact
        return person_project_impact

    def to_dict(self):
        ret = self.package.as_snippet
        ret["roles"] = [r.role for r in self.roles]
        ret["person_project_credit"] = self.person_project_credit
        ret["person_project_commits"] = self.person_project_commits
        ret["person_project_impact"] = self.person_project_impact
        return ret

    @property
    def as_person_snippet(self):
        ret = self.package.as_snippet_without_people
        ret["roles"] = [r.role for r in self.roles]
        ret["person_project_credit"] = self.person_project_credit
        ret["person_project_commits"] = self.person_project_commits
        ret["person_project_impact"] = self.person_project_impact
        return ret




def find_best_match(persons, **kwargs):
    # get them in this priority order
    for person in persons:
        if "github_login" in kwargs and kwargs["github_login"]:
            if person.github_login == kwargs["github_login"]:
                print "\n matched on github_login"
                return person

    for person in persons:
        if "email" in kwargs and kwargs["email"]:
            if person.email == kwargs["email"]:
                print "\n matched on email"
                return person

    for person in persons:
        if "name" in kwargs and kwargs["name"]:
            normalized_person_name = person.name.replace(".", "")
            normalized_match_name = kwargs["name"].replace(".", "")
            if normalized_person_name == normalized_match_name:
                print "\n matched on exact name"
                return person
    
    return None


def get_or_make_person(**kwargs):
    res = None

    if 'name' in kwargs and kwargs["name"] == "UNKNOWN":
        # pypi sets unknown people to have the name "UNKNOWN"
        # we don't want to make tons of these, it's just one 'person'.
        res = db.session.query(Person).filter(
            Person.name == "UNKNOWN"
        ).first()

    if 'name' in kwargs and kwargs["name"] == "ORPHANED":
        # cran sets this when the maintainer is gone.
        # we don't want to make tons of these, it's just one 'person'.
        res = db.session.query(Person).filter(
            Person.name == "ORPHANED"
        ).first()

    if res is not None:
        return res

    or_filters = []

    if "github_login" in kwargs and kwargs["github_login"]:
        or_filters.append(Person.github_login == kwargs["github_login"])

    elif "email" in kwargs and kwargs["email"]:
        or_filters.append(Person.email == kwargs["email"])

    elif "name" in kwargs and kwargs["name"]:
        incoming_parsed_name = HumanName(kwargs["name"])
        dict_for_matching = {
            "first": incoming_parsed_name.first,
            "last": incoming_parsed_name.last}
        or_filters.append(Person.parsed_name.contains(dict_for_matching))

    if or_filters:
        query = db.session.query(Person).filter(or_(*or_filters))
        persons = query.all()
        res = find_best_match(persons, **kwargs)

    if res is not None:
        return res
    else:
        print u"minting a new person using {}".format(kwargs)
        new_person = Person(**kwargs)
        # do person attrib setting now so that can use them to detect dedups later this run
        # set_github_about sets name so has to go before parsed name

        keep_trying_github_call = True
        while keep_trying_github_call:
            try:
               new_person.set_github_about() 
               keep_trying_github_call = False
            except GithubRateLimitException:
               print "all github keys maxed out. sleeping...."
               sleep(5 * 60)
               print "trying github call again, mabye api keys refreshed?".format(url)

        new_person.set_parsed_name()

        db.session.add(new_person)

        #need this commit to handle matching people added previously in this chunk
        db.session.commit()  
        return new_person






