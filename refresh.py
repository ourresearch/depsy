import requests
from lxml import html
from app import db
from models.cran_package import CranPackage
from models.pypi_package import PypiPackage


def add_all_new_packages(package_class):

    all_current_package_id_rows = db.session.query(package_class.id).all()
    all_current_package_ids = [row[0] for row in all_current_package_id_rows]

    all_names = package_class.get_all_live_package_names()

    for package_name in all_names:
        new_package = package_class(project_name=package_name)
        if new_package.id not in all_current_package_ids:
            print "\n\nadded new package:", new_package.id
            new_package.refresh()
            db.session.add(new_package)
            db.session.commit()

    print len(all_names)



def add_all_new_github_repos(language):
    date = start_date
    while date <= end_date:
        next_date = date + timdelta(days=1)
        url_template = "https://api.github.com/search/repositories?q=created:%22{date}%20..%20{next_date}%22%20language:{language}&per_page=1000&sort=forks&order=desc"
        url = url_template.format(
            language=language, date=date, next_date=next_date)
        r = requests.get(url)
        data = r.json()
        date = next_date


if __name__ == '__main__':

    # add_all_new_packages(CranPackage)
    add_all_new_packages(PypiPackage)

    # start_date = ""
    # end_date = ""
    # add_all_new_github_repos("R", start_date, end_date)

    # call run_igraph.sh
    # go through all
