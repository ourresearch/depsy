from app import db
from sqlalchemy.dialects.postgresql import JSONB
from models.github_api import ZipGetter



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


    def set_dependency_lines(self):
        getter = github_zip_getter_factory(self.login, self.repo_name)
        getter.get_dep_lines(self.language)

        self.dependency_lines = getter.dep_lines
        self.zip_download_elapsed = getter.download_elapsed
        self.zip_download_size = getter.download_kb
        self.zip_download_error = getter.error
        self.zip_grep_elapsed = getter.grep_elapsed

        return self.dependency_lines


    def zip_getter(self):
        if not self.api_raw:
            return None
        if not "url" in self.api_raw:
            return None

        url = self.api_raw["url"]
        getter = ZipGetter(url)
        return getter


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




















def test_pypi_project():
    print "testing pypi project!"