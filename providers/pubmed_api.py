import requests

# class Querier:
#     pass

# class PmcQuerier(Querier):
#     pass


def get_hits_from_europe_pmc(query):
    pmc_api_url_template = "http://www.ebi.ac.uk/europepmc/webservices/rest/search/query={query}&pageSize=1000&format=json&resulttype=idlist"
    url = pmc_api_url_template.format(query=query)
    try:
        print u"calling PMC with {}".format(url)
        r = requests.get(url)
    except requests.exceptions.RequestException:
        print "RequestException, failed on", url
        return None

    print r
    results = r.json()
    if results["hitCount"] == 0:
        pmc_mentions = []
    else:
        pmc_mentions = [r["pmid"] for r in results["resultList"]["result"]]
        print "found some!!!", pmc_mentions
    return pmc_mentions    