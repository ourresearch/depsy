from app import db
from sqlalchemy.dialects.postgresql import JSONB
from models.github_api import ZipGetter
import requests
import re
import pickle
from pathlib import Path
from time import time
from util import elapsed

class PypiProject(db.Model):
    project_name = db.Column(db.Text, primary_key=True)
    owner_name = db.Column(db.Text)

    github_owner = db.Column(db.Text)
    github_repo_name = db.Column(db.Text)

    api_raw = db.Column(JSONB)
    reverse_deps = db.Column(JSONB)
    deps = db.Column(JSONB)

    zip_download_elapsed = db.Column(db.Float)
    zip_download_size = db.Column(db.Integer)
    zip_download_error = db.Column(db.Text)

    dependency_lines = db.Column(db.Text)
    zip_grep_elapsed = db.Column(db.Float)

    def __repr__(self):
        return u'<PypiProject {project_name}>'.format(
            project_name=self.project_name)

    @property
    def language(self):
        return "python"


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





def get_pypi_package_names():
    start_time = time()
    pypi_q = db.session.query(PypiProject.project_name)
    pypi_lib_names = [r[0] for r in pypi_q.all()]

    print "got {} PyPi project names in {}sec.".format(
        len(pypi_lib_names),
        elapsed(start_time)
    )

    return pypi_lib_names













