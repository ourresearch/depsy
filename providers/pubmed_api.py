import requests
import re

# class Querier:
#     pass

# class PmcQuerier(Querier):
#     pass


def get_hits_from_europe_pmc(query):
    query_template = "http://www.ebi.ac.uk/europepmc/webservices/rest/search/query={query}&pageSize=1000&format=json&resulttype=idlist"
    url = query_template.format(query=query)
    try:
        print u"calling PMC with {}".format(url)
        r = requests.get(url)
    except requests.exceptions.RequestException:
        print "RequestException, failed on", url
        return None

    results = r.json()
    try:
        hits = results["hitCount"]
    except KeyError:
        hits = 0
    return hits    

def get_hits_from_arxiv(query):
    query_template = "http://search.arxiv.org:8081/?query={query}web/packages/knitr&in="
    url = query_template.format(query=query)
    try:
        print u"calling arXiv with {}".format(url)
        r = requests.get(url)
    except requests.exceptions.RequestException:
        print "RequestException, failed on", url
        return None

    page = r.text
    hit_sentences = re.findall(ur"Displaying hits \d+ to \d+ of (\d+)", page)
    try:
        hits = hit_sentences[0]
    except KeyError:
        hits = 0
    return hits     