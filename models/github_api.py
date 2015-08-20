import os
import logging
import requests

logger = logging.getLogger("github_api")

tokens_str = os.environ["GITHUB_TOKENS"]
token_pairs = [t.split(":") for t in tokens_str.split(",")]

def make_call(url, token_pair):
    r = requests.get(url, auth=(token_pair[0], token_pair[1]))

    logger.info(
        "{status_code}: {url}.  {rate_limit} calls remain for {username}".format(
            status_code=r.status_code,
            url=url,
            rate_limit=r.headers["X-RateLimit-Remaining"],
            username=token_pair[0]
        )
    )

    # this will raise a 404 if there was a 404,
    # and a 403 if rate limit exceeded
    r.raise_for_status()
    return r.json()


def get_profile(username):
    url = "https://api.github.com/users/{username}".format(
        username=username
    )



