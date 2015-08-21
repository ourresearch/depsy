from app import db
from models.pypi_repo import PyPiRepo
from models.github_api import username_and_repo_name_from_github_url
from util import update_sqla_objects
from util import get_sqla_objects
from time import time





def add_github_repo_name_info(repo):
    username, repo_name = username_and_repo_name_from_github_url(repo.github_url)
    repo.github_repo_owner = username
    repo.github_repo_name = repo_name
    return repo

def get_repo_meta(owner_name, repo_name):
    pass

def get_repo_contribs(owner_name, repo_name):
    pass




def main():
    q = db.session.query(PyPiRepo).filter(PyPiRepo.github_url.isnot(None))
    repos = q.all()
    update_sqla_objects(repos, add_github_repo_name_info)




if __name__ == '__main__':
    overall_start = time()
    main()
    print "script done in {} sec.".format(round(time() - overall_start, 2))





















