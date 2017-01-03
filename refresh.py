import requests
from lxml import html
from app import db
from models.cran_package import CranPackage

#useful info: http://www.r-pkg.org/services
def seed_all_cran_packages():
    # maybe there is a machine readable version of this?  I couldn't find it.
    url = "https://cran.r-project.org/web/packages/available_packages_by_name.html"
    r = requests.get(url)
    print "got page"

    page = r.text
    tree = html.fromstring(page)
    print "finished parsing"
    all_names = tree.xpath('//tr/td[1]/a/text()')
    all_current_package_id_rows = db.session.query(CranPackage.id).all()
    all_current_package_ids = [row[0] for row in all_current_package_id_rows]
    print all_current_package_ids[0:10]
    for package_name in all_names:
        package = CranPackage(project_name=package_name)
        if package.id not in all_current_package_ids:
            print "added new package:", package_name
            db.session.add(package)
            db.session.commit()
    print len(all_names)



if __name__ == '__main__':

    seed_all_cran_packages()