import requests
import re

from lxml import html


class FullTextSource:

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def run_query(self, query):
        try:
            url = self.query_url(query)
            print u"calling {} with {}".format(self.__class__.__name__, url)
            r = requests.get(url)
        except requests.exceptions.RequestException:
            print "RequestException, failed on", url
            return None

        return self.extract_results(r)


class Pmc(FullTextSource):
    def query_url(self, query):
        query_template = "http://www.ebi.ac.uk/europepmc/webservices/rest/search/query={query}&pageSize=1000&format=json&resulttype=idlist"
        url = query_template.format(query=query)
        return url

    def extract_results(self, request_response):
        results = request_response.json()
        try:
            hits = int(results["hitCount"])
        except KeyError:
            hits = 0
        return hits   


class Arxiv(FullTextSource):
    def query_url(self, query):
        query_template = "http://search.arxiv.org:8081/?query={query}"
        url = query_template.format(query=query)
        return url

    def extract_results(self, request_response):
        page = request_response.text
        hit_sentences = re.findall(ur"Displaying hits \d+ to \d+ of (\d+)", page)
        try:
            hits = int(hit_sentences[0])
        except IndexError:
            hits = 0
        return hits     


class Citeseer(FullTextSource):
    def query_url(self, query):
        query_template = "http://citeseerx.ist.psu.edu/search?q={query}+NOT+Maintainer&submit=Search&sort=rlv&t=doc"
        url = query_template.format(query=query)
        return url

    def extract_results(self, request_response):
        page = request_response.text
        tree = html.fromstring(page)
        data = {}
        result_info = tree.xpath('//*[@id="result_info"]/strong/text()')
        try:
            hits = int(result_info[1])
        except (IndexError, ValueError):
            hits = 0
        return hits      



