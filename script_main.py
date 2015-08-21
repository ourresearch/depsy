from time import time

from models.pypi_repo import save_all_repo_owners_and_key_committers


def main():
    #return save_all_repo_owners()
    save_all_repo_owners_and_key_committers()

if __name__ == '__main__':
    overall_start = time()
    main()
    print "script done in {} sec.".format(round(time() - overall_start, 2))


