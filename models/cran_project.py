from app import db
from sqlalchemy.dialects.postgresql import JSONB
import requests
from lxml import html
import re



class CranProject(db.Model):
    project_name = db.Column(db.Text, primary_key=True)
    owner_name = db.Column(db.Text)

    github_owner = db.Column(db.Text)
    github_repo_name = db.Column(db.Text)

    api_raw = db.Column(JSONB)
    downloads = db.Column(JSONB)
    reverse_deps = db.Column(JSONB)
    deps = db.Column(JSONB)
    proxy_papers = db.Column(db.Text)

    def __repr__(self):
        return u'<CranProject {project_name}>'.format(
            project_name=self.project_name)

    def set_cran_about(self):
        url_template = "http://crandb.r-pkg.org/%s"
        data_url = url_template % self.project_name
        print data_url
        response = requests.get(data_url)
        self.api_raw = response.json()


    def set_downloads(self):
        url_template = "http://cranlogs.r-pkg.org/downloads/daily/1900-01-01:2020-01-01/%s"
        data_url = url_template % self.project_name
        print data_url
        response = requests.get(data_url)
        if "day" in response.text:
            data = {}
            all_days = response.json()[0]["downloads"]
            data["total_downloads"] = sum([int(day["downloads"]) for day in all_days])
            data["first_download"] = min([day["day"] for day in all_days])
            data["daily_downloads"] = all_days
        else:
            data = {"total_downloads": 0}
        self.downloads = data


    def set_reverse_depends(self):
        url_template = "https://cran.r-project.org/web/packages/%s/"
        data_url = url_template % self.project_name
        print data_url

        # this call keeps timing out for some reason.  quick workaround:
        response = None
        while not response:
            try:
                response = requests.get(data_url)
            except requests.exceptions.ConnectionError:
                # try again
                print "connection timed out, trying again"
                pass

        if "Reverse" in response.text:
            page = response.text
            page = page.replace("&nbsp;", " ")  # otherwise starts-with for lxml doesn't work
            tree = html.fromstring(page)
            data = {}
            data["reverse_imports"] = tree.xpath('//tr[(starts-with(td[1], "Reverse imports"))]/td[2]/a/text()')
            data["reverse_depends"] = tree.xpath('//tr[(starts-with(td[1], "Reverse depends"))]/td[2]/a/text()')
            data["reverse_suggests"] = tree.xpath('//tr[(starts-with(td[1], "Reverse suggests"))]/td[2]/a/text()')
            data["reverse_enhances"] = tree.xpath('//tr[(starts-with(td[1], "Reverse enhances"))]/td[2]/a/text()')
            all_reverse_deps = set(data["reverse_imports"] + data["reverse_depends"] + data["reverse_suggests"] + data["reverse_enhances"])
            data["all_reverse_deps"] = list(all_reverse_deps)

        else:
            data = {"all_reverse_deps": []}
        self.reverse_deps = data


    def set_proxy_papers(self):
        url_template = "https://cran.r-project.org/web/packages/%s/citation.html"
        data_url = url_template % self.project_name
        print data_url

        # this call keeps timing out for some reason.  quick workaround:
        response = None
        while not response:
            try:
                response = requests.get(data_url, timeout=10)
            except requests.exceptions.ConnectionError:
                # try again
                print "connection timed out, trying again"
                pass

        if response.status_code==200 and "<pre>" in response.text:
            page = response.text
            tree = html.fromstring(page)
            proxy_papers = str(tree.xpath('//pre/text()'))
            print proxy_papers
        else:
            print "no proxy paper found"
            proxy_papers = "No proxy paper"
        self.proxy_papers = proxy_papers


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
    for project_name in all_names:
        print project_name
        project = CranProject(project_name=project_name)
        db.session.add(project)
        db.session.commit()


"""
add cran download stats
"""
def add_cran_downloads(project_name):
    project = db.session.query(CranProject).get(project_name)
    project.set_downloads()
    if project.downloads:
        print "got downloads!"
    db.session.commit()
    # print u"download data found: {}".format(project.downloads)

def add_all_cran_downloads():
    q = db.session.query(CranProject.project_name)
    q = q.filter(CranProject.downloads == "null")
    q = q.order_by(CranProject.project_name)

    for row in q.all():
        add_cran_downloads(row[0])


"""
add cran reverse_deps
"""
def add_cran_reverse_deps(project_name):
    project = db.session.query(CranProject).get(project_name)
    project.set_reverse_depends()
    if project.reverse_deps:
        print "got reverse_deps!"
    db.session.commit()
    print u"data found: {}".format(project.reverse_deps)


def add_all_cran_reverse_deps():
    q = db.session.query(CranProject.project_name)
    q = q.filter(CranProject.reverse_deps == "null")
    q = q.order_by(CranProject.project_name)

    for row in q.all():
        add_cran_reverse_deps(row[0])


"""
add cran about
"""
def add_cran_about(project_name):
    project = db.session.query(CranProject).get(project_name)
    project.set_cran_about()
    if project.api_raw:
        print "got api_raw!"
    db.session.commit()
    print u"data found: {}".format(project.api_raw)


def add_all_cran_about():
    q = db.session.query(CranProject.project_name)
    q = q.filter(CranProject.api_raw == "null")
    q = q.order_by(CranProject.project_name)

    for row in q.all():
        add_cran_about(row[0])


"""
add cran proxy papers
"""
def add_cran_proxy_papers(project_name):
    project = db.session.query(CranProject).get(project_name)
    project.set_proxy_papers()
    if project.proxy_papers:
        print "got proxy_papers!"
    db.session.commit()


def add_all_cran_proxy_papers():
    q = db.session.query(CranProject.project_name)
    q = q.filter(CranProject.proxy_papers == None)
    q = q.order_by(CranProject.project_name)

    for row in q.all():
        add_cran_proxy_papers(row[0])












def test_cran_project():
    print "testing cran project!"