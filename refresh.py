import requests
import argparse
import datetime

from app import db
from models.cran_package import CranPackage
from models.pypi_package import PypiPackage
from models.github_repo import GithubRepo
from models.github_api import make_ratelimited_call
import update
from util import safe_commit


def add_all_new_packages(package_class):

    all_current_package_id_rows = db.session.query(package_class.id).all()
    all_current_package_ids = [row[0] for row in all_current_package_id_rows]

    all_names = package_class.get_all_live_package_names()

    for package_name in all_names:
        new_package = package_class(project_name=package_name)
        if new_package.id not in all_current_package_ids:
            print "\n\nadded new package:", new_package.id
            # new_package.refresh()
            db.session.add(new_package)
            safe_commit(db)

    print len(all_names)



def add_all_new_github_repos(language):
    all_current_github_repo_rows = db.session.query(GithubRepo.id).filter(GithubRepo.language==language).all()
    all_current_github_repo_ids = [row[0] for row in all_current_github_repo_rows]

    end_date = datetime.datetime(2015, 11, 01)
    start_date = datetime.datetime.utcnow()
    date = start_date
    while date >= end_date:
        prev_date = date - datetime.timedelta(days=1)
        # The sort field. One of stars, forks, or updated.
        # max of 100 returned
        # authenticated rate limit: 30/min
        sort_fragements = [
            "sort=stars&order=desc",
            "sort=updated&order=desc",
            "sort=forks&order=desc",
            "sort=stars&order=asc",
            "sort=updated&order=asc",
            "sort=forks&order=asc"
            ]
        for sort_fragment in sort_fragements:
            url_template = "https://api.github.com/search/repositories?q=created:%22{prev_date}%20..%20{date}%22%20language:{language}&per_page=1000&{sort_fragment}"
            url = url_template.format(
                language=language,
                date=date.isoformat()[0:10],
                prev_date=prev_date.isoformat()[0:10],
                sort_fragment=sort_fragment)
            print url
            data = make_ratelimited_call(url)
            print date.isoformat()[0:10], data["total_count"], data["incomplete_results"]
            date = prev_date
            for repo_dict in data["items"]:
                new_repo = GithubRepo(login=repo_dict["owner"]["login"], repo_name=repo_dict["name"], language=language)
                new_repo.api_raw = repo_dict
                print "new_repo:", new_repo
                if new_repo.id not in all_current_github_repo_ids:
                    print "added new repo from {}: {}\n".format(date.isoformat()[0:10], new_repo.id)
                    db.session.add(new_repo)
                    all_current_github_repo_ids.append(new_repo.id)
            safe_commit(db)




def recalculate_everything(parsed_args):
    if parsed_args.language=="r":
        package_class = CranPackage
    else:
        package_class = PypiPackage

    parsed_args.fn = u"{}.recalculate".format(package_class.__name__)
    print "parsed_args.fn", parsed_args.fn
    update.run_update(parsed_args)


def refresh(parsed_args):
    if parsed_args.language=="r":
        package_class = CranPackage
    else:
        package_class = PypiPackage

    parsed_args.fn = u"{}.refresh".format(package_class.__name__)
    print "parsed_args.fn", parsed_args.fn
    update.run_update(parsed_args)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Run stuff.")
    parser.add_argument('language', help="r or python")
    parsed_args = update.parse_update_optional_args(parser)


    add_all_new_github_repos(parsed_args.language)

    # add_all_new_packages(PypiPackage)
    # add_all_new_packages(CranPackage)


    # start_date = ""
    # end_date = ""
    # add_all_new_github_repos("R", start_date, end_date)

    # call run_igraph.sh
    # go through all

    # recalculate everything
    # recalculate_everything(parsed_args)