from app import db
from sqlalchemy.dialects.postgresql import JSONB
from models import github_api
import requests
import re
import pickle
from pathlib import Path
from time import time
from util import elapsed

# set to nothing most of the time, so imports work
pypi_package_names = None
# comment this out here now, because usually not using
#pypi_package_names = get_pypi_package_names()

class PypiProject(db.Model):
    project_name = db.Column(db.Text, primary_key=True)
    owner_name = db.Column(db.Text)

    github_owner = db.Column(db.Text)
    github_repo_name = db.Column(db.Text)
    github_contributors = db.Column(JSONB)

    api_raw = db.Column(JSONB)
    reverse_deps = db.Column(JSONB)
    deps = db.Column(JSONB)

    zip_download_elapsed = db.Column(db.Float)
    zip_download_size = db.Column(db.Integer)
    zip_download_error = db.Column(db.Text)

    #dependency_lines = db.Column(db.Text)
    #zip_grep_elapsed = db.Column(db.Float)

    def __repr__(self):
        return u'<PypiProject {project_name}>'.format(
            project_name=self.project_name)

    @property
    def language(self):
        return "python"

    def set_github_contributors(self):
        self.github_contributors = github_api.get_repo_contributors(
            self.github_owner,
            self.github_repo_name
        )
        print "added github contributors!"
        print self.github_contributors


    #def set_dependency_lines(self):
    #    getter = github_zip_getter_factory(self.login, self.repo_name)
    #    getter.get_dep_lines(self.language)
    #
    #    self.dependency_lines = getter.dep_lines
    #    self.zip_download_elapsed = getter.download_elapsed
    #    self.zip_download_size = getter.download_kb
    #    self.zip_download_error = getter.error
    #    self.zip_grep_elapsed = getter.grep_elapsed
    #
    #    return self.dependency_lines
    #
    #
    #def zip_getter(self):
    #    if not self.api_raw:
    #        return None
    #    if not "url" in self.api_raw:
    #        return None
    #
    #    url = self.api_raw["url"]
    #    getter = ZipGetter(url)
    #    return getter


"""
add pypi dependency lines
"""
def add_pypi_dependency_lines(project_name):
    project = db.session.query(PypiProject).get(project_name)
    if project is None:
        print "there's no pypi project called {}".format(project_name)
        return False

    project.set_dependency_lines()
    db.session.commit()


def add_all_pypi_dependency_lines():
    q = db.session.query(PypiProject.project_name)
    q = q.filter(~PypiProject.api_raw.has_key('error_code'))
    q = q.filter(PypiProject.dependency_lines == None, 
        PypiProject.zip_download_error == None, 
        PypiProject.zip_download_elapsed == None)
    q = q.order_by(PypiProject.project_name)

    for row in q.all():
        #print "setting this row", row
        add_pypi_dependency_lines(row[0], row[1])








"""


database and file operations.

"""


class PythonStandardLibs():
    url = "https://docs.python.org/2.7/py-modindex.html"
    data_dir = Path(__file__, "../../data").resolve()
    pickle_path = Path(data_dir, "python_standard_libs.pickle")

    @classmethod
    def save_from_web(cls):  
        # only needs to be used once ever, here for tidiness
        # checked the result into source control as python_standard_libs.pickle
        html = requests.get(cls.url).text
        exp = r'<tt class="xref">([^<]+)'
        matches = re.findall(exp, html)
        libs = [m for m in matches if '.' not in m]

        with open(str(cls.pickle_path), "w") as f:
            pickle.dump(libs, f)

        print "saved these to file: {}".format(libs)

    @classmethod
    def get(cls):
        with open(str(cls.pickle_path), "r") as f:
            return pickle.load(f)


def save_python_standard_libs():
    PythonStandardLibs.save_from_web()

    # to show the thing works
    print "got these from pickled file: {}".format(PythonStandardLibs.get())





def get_pypi_package_names(force_lower=True):
    """
        returns a dict with the key as the lowercase name and the value as the orig cased name
    """
    start_time = time()
    pypi_q = db.session.query(PypiProject.project_name)
    pypi_lib_names = [r[0] for r in pypi_q.all()]

    pypi_lib_lookup = dict([(name.lower(), name) for name in pypi_lib_names])

    print "got {} PyPi project names in {}sec.".format(
        len(pypi_lib_lookup),
        elapsed(start_time)
    )

    return pypi_lib_lookup






"""
get github contrib info
"""

def set_all_pypi_github_contributors(limit=100):
    q = db.session.query(PypiProject.project_name)
    q = q.filter(PypiProject.github_repo_name != None)
    q = q.filter(PypiProject.github_contributors == None)
    q = q.order_by(PypiProject.project_name)
    q = q.limit(limit)

    update_fn = make_update_fn("set_github_contributors")

    for row in q.all():
        update_fn(row[0])


def make_update_fn(method_name):
    def fn(obj_id):
        start_time = time()

        obj = db.session.query(PypiProject).get(obj_id)
        if obj is None:
            return None

        method_to_run = getattr(obj, method_name)
        method_to_run()

        db.session.commit()

        print "ran {repr}.{method_name}() method  and committed. took {elapsted}sec".format(
            repr=obj,
            method_name=method_name,
            elapsted=elapsed(start_time, 4)
        )
        return None  # important for if we use this on RQ

    return fn













