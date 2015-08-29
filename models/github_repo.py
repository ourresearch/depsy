from app import db
from app import github_zip_queue
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import DataError
from sqlalchemy import or_

from models import github_api
from models.github_api import username_and_repo_name_from_github_url
from models.github_api import github_zip_getter_factory
from models.pypi_project import PypiProject
from models.pypi_project import PythonStandardLibs

from models import github_api
import requests
from util import elapsed
from time import time
from time import sleep
import ast
import subprocess


class GithubRepo(db.Model):
    login = db.Column(db.Text, primary_key=True)
    repo_name = db.Column(db.Text, primary_key=True)
    language = db.Column(db.Text)
    api_raw = db.Column(JSONB)
    dependency_lines = db.Column(db.Text)
    zip_download_elapsed = db.Column(db.Float)
    zip_download_size = db.Column(db.Integer)
    zip_download_error = db.Column(db.Text)
    zip_grep_elapsed = db.Column(db.Float)
    pypi_dependencies = db.Column(JSONB)

    def __repr__(self):
        return u'<GithubRepo {language} {login}/{repo_name}>'.format(
            language=self.language, login=self.login, repo_name=self.repo_name)

    def set_github_about(self):
        self.api_raw = github_api.get_repo_data(self.login, self.repo_name)
        return self.api_raw

    def set_github_dependency_lines(self):

        getter = github_zip_getter_factory(self.login, self.repo_name)
        getter.get_dep_lines(self.language)

        self.dependency_lines = getter.dep_lines
        self.zip_download_elapsed = getter.download_elapsed
        self.zip_download_size = getter.download_kb
        self.zip_download_error = getter.error
        self.zip_grep_elapsed = getter.grep_elapsed

        return self.dependency_lines


    @property
    def full_name(self):
        return self.login + "/" + self.repo_name

    def set_save_error(self):
        # the db threw an error when we tried to save this.
        # likely a 'invalid byte sequence for encoding "UTF8"'
        self.zip_download_error = "save_error"

    def set_pypi_dependencies(self, pypi_lib_names):
        """
        using self.dependency_lines, finds all pypi libs imported by repo.

        ignores libs that are part of the python 2.7 standard library, even
        if they are on pypi

        known false-positive issues:
        * counts imports of local libs that have the same name as pypi libs.
          this is a serious problem for common local-library names like
          'models', 'utils', 'config', etc
        * counts imports within multi-line quote comments.

        known false-negative issues:
        * ignores imports done with importlib.import_module
        * ignores dynamic importing techniques like map(__import__, moduleNames)
        """
        start_time = time()
        lines = self.dependency_lines.split("\n")
        import_lines = [l.split(":")[1] for l in lines if ":" in l]
        modules_imported = set()
        for line in import_lines:
            print "checking this line: {}".format(line)
            try:
                nodes = ast.parse(line.strip()).body
            except SyntaxError:
                # not well-formed python...prolly part of a comment str
                continue

            try:
                node = nodes[0]
            except IndexError:
                continue

            # from foo import bar # finds foo
            if isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    # relative imports unlikely to be from PyPi
                    continue
                modules_imported.add(node.name)

            # import foo, bar  # finds foo, bar
            elif isinstance(node, ast.Import):
                for my_name in node.names:
                    modules_imported.add(my_name.name)


        for module_name in modules_imported:
            pypi_package = self._get_pypi_package(module_name, pypi_lib_names)
            if pypi_package is not None:
                self.pypi_dependencies.append(pypi_package)

        print "done finding pypi deps for {}: {} (took {}sec)".format(
            self.full_name,
            self.pypi_dependencies,
            elapsed(start_time, 4)
        )
        return self.pypi_dependencies

    def _get_pypi_package(self, module_name, pypi_lib_names):

        # if it's in the standard lib it doesn't count--even if in might be in pypi
        if module_name in PythonStandardLibs.get():
            return None

        # great, we found one!
        if module_name in pypi_lib_names:
            return module_name

        # if foo.bar.baz is not in pypi, maybe foo.bar is. let's try that.
        elif '.' in module_name:
            shortened_name = module_name.split('.')[-1]
            return self._get_pypi_package(shortened_name, pypi_lib_names)

        # if there's no dot in your name, there are no more options, you're done
        else:
            return None











"""
add the github repo-about api info
"""
def add_github_about(login, repo_name):
    repo = db.session.query(GithubRepo).get((login, repo_name))
    repo.set_github_about()
    db.session.commit()

    print repo

def add_all_github_about():
    q = db.session.query(GithubRepo.login, GithubRepo.repo_name)
    q = q.filter(GithubRepo.api_raw == 'null')
    q = q.order_by(GithubRepo.login)

    for row in q.all():
        #print "setting this row", row
        add_github_about(row[0], row[1])






"""
add github dependency lines
"""
def add_github_dependency_lines(login, repo_name):
    repo = get_repo(login, repo_name)
    if repo:
        repo.set_github_dependency_lines()
        commit_repo(repo)
    return None  # important that it returns None for RQ


def add_all_github_dependency_lines(q_limit=100):
    q = db.session.query(GithubRepo.login, GithubRepo.repo_name)
    q = q.filter(~GithubRepo.api_raw.has_key('error_code'))
    q = q.filter(GithubRepo.zip_download_error == None)
    q = q.filter(GithubRepo.zip_download_elapsed == None)
    q = q.order_by(GithubRepo.login)
    q = q.limit(q_limit)

    return enque_repos(q, add_github_dependency_lines)







"""
find and save list of pypi dependencies for each repo
"""
def set_pypi_dependencies(login, repo_name):
    start_time = time()
    repo = get_repo(login, repo_name)
    if repo is None:
        return None

    pypi_q = db.session.query(PypiProject.project_name)
    pypi_lib_names = [r[0] for r in pypi_q.all()]
    num_pypi_lib_names = len(pypi_lib_names)
    print "got {} PyPi project names in {}sec.".format(
        num_pypi_lib_names,
        elapsed(start_time)
    )

    repo.set_pypi_dependencies(pypi_lib_names)
    commit_repo(repo)
    print "found deps and committed. took {}sec".format(elapsed(start_time), 4)
    return None  # important that it returns None for RQ


def set_all_pypi_dependencies(q_limit=100):
    q = db.session.query(GithubRepo.login, GithubRepo.repo_name)
    q = q.filter(GithubRepo.dependency_lines != None)
    q = q.filter(GithubRepo.pypi_dependencies == None)
    q = q.filter(GithubRepo.language == "python")
    q = q.order_by(GithubRepo.login)
    q = q.limit(q_limit)

    return enque_repos(q, set_pypi_dependencies)






"""
utility functions
"""

def enque_repos(q, fn, *args):
    """
    Takes sqlalchemy query with (login, repo_name) IDs, runs fn on those repos.
    """
    empty_github_zip_queue()

    start_time = time()
    index = 0

    print "running this query: \n{}\n".format(
        q.statement.compile(dialect=postgresql.dialect())
    )
    row_list = q.all()
    num_jobs = len(row_list)
    print "finished query in {}sec".format(elapsed(start_time))
    print "adding {} jobs to queue...".format(num_jobs)

    for row in row_list:
        row_args = (row[0], row[1])
        row_args += args  # pass incoming option args to the enqueued function

        job = github_zip_queue.enqueue_call(
            func=fn,
            args=row_args,
            result_ttl=0  # number of seconds
        )
        job.meta["full_repo_name"] = row[0] + "/" + row[1]
        job.save()
        if index % 1000 == 0:
            print "added {} jobs to queue in {}sec".format(
                index,
                elapsed(start_time)
            )
        index += 1
    print "last repo added to the queue was {}".format(row[0] + "/" + row[1])

    monitor_github_zip_queue(start_time, num_jobs)
    return True


def get_repo(login, repo_name):
    repo = db.session.query(GithubRepo).get((login, repo_name))
    if repo is None:
        print "there's no repo called {}/{}".format(login, repo_name)
    return repo


def commit_repo(repo):
    try:
        db.session.commit()
    except DataError:
        db.session.rollback()
        repo.set_save_error()
        db.session.commit()


def monitor_github_zip_queue(start_time, num_jobs):
    current_count = github_zip_queue.count
    time_per_job = 1
    while current_count:
        sleep(1)
        current_count = github_zip_queue.count
        done = num_jobs - current_count
        try:
            time_per_job = elapsed(start_time) / done
        except ZeroDivisionError:
            pass

        mins_left = int(current_count * time_per_job / 60)

        print "finished {done} jobs in {elapsed} min. {left} left (est {mins_left}min)".format(
            done=done,
            elapsed=int(elapsed(start_time) / 60),
            mins_left=mins_left,
            left=current_count
        )
    print "Done! {} jobs took {} seconds (avg {} secs/job)".format(
        num_jobs,
        elapsed(start_time),
        time_per_job
    )
    return True


def empty_github_zip_queue():
    print "emptying {} jobs on the github zip queue....".format(github_zip_queue.count)
    github_zip_queue.empty()
    print "done. there's {} jobs on the github zip queue now.".format(github_zip_queue.count)










"""
populate the github_repo table from a remote CSV with repo names
"""
# call python main.py add_python_repos_from_google_bucket to run
def add_python_repos_from_google_bucket():
    url = "https://storage.googleapis.com/impactstory/github_python_repo_names.csv"
    add_repos_from_remote_csv(url, "python")

# call python main.py add_r_repos_from_google_bucket to run
def add_r_repos_from_google_bucket():
    url = "https://storage.googleapis.com/impactstory/github_r_repo_names.csv"
    add_repos_from_remote_csv(url, "r")

def add_repos_from_remote_csv(csv_url, language):
    start = time()

    print "going to go get file"
    response = requests.get(csv_url, stream=True)
    index = 0

    for github_url in response.iter_lines(chunk_size=1000):
        login, repo_name = username_and_repo_name_from_github_url(github_url)
        if login and repo_name:
            repo = GithubRepo(
                login=login,
                repo_name=repo_name,
                language=language
            )
            print repo
            db.session.merge(repo)
            index += 1
            if index % 1000 == 0:
                db.session.commit()
                print "flushing on index {index}, elapsed: {elapsed}".format(
                    index=index,
                    elapsed=elapsed(start))

    db.session.commit()

























