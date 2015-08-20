from app import db
from models.pypi_repo import PyPiRepo

def page_query(q, page_size=1000):
    offset = 0
    while True:
        r = False
        for elem in q.limit(page_size).offset(offset):
            r = True
            yield elem
        offset += page_size
        if not r:
            break



def get_github_repo_urls():
    print "getting github repo urls..."
    q = db.session.query(PyPiRepo.github_repo)\
        .filter(PyPiRepo.github_repo.isnot(None))

    ret = [url for url in page_query(q)]
    return ret



def main():
    github_repos = get_github_repo_urls()
    print "got {} github repos".format(len(github_repos))


if __name__ == '__main__':


    main()
    print "script done, exiting."





















