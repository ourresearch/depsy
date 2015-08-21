from time import time

from models.pypi_repo import save_all_repo_owners


def main():
    return save_all_repo_owners()

if __name__ == '__main__':
    overall_start = time()
    main()
    print "script done in {} sec.".format(round(time() - overall_start, 2))


