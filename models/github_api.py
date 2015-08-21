import os
import logging
import requests
from urlparse import urlparse
from random import shuffle
from app import db


logger = logging.getLogger("github_api")

class GithubApiKeys():
    def __init__(self):
        self.keys = self._get_api_keys()
        self.current = 0

    def get(self):
        try:
            return self.keys[self.current]
        except IndexError:
            return None

    def reset(self):
        self.current = 0

    def next(self):
        self.current += 1
        return self.get()

    def _get_api_keys(self):
        tokens_str = os.environ["GITHUB_TOKENS"]
        token_pairs = [t.split(":") for t in tokens_str.split(",")]

        # the shuffle means different threads will start w different keys.
        shuffle(token_pairs)
        return token_pairs


global_keys = GithubApiKeys()

class GithubRateLimitException(Exception):
    pass


def make_call(url):

    try:
        key_owner, key_token = global_keys.get()
    except TypeError:  # there are no more keys.
        raise GithubRateLimitException


    r = requests.get(url, auth=(key_owner, key_token))

    logger.info(
        "{status_code}: {url}.  {rate_limit} calls remain for {username}".format(
            status_code=r.status_code,
            url=url,
            rate_limit=r.headers["X-RateLimit-Remaining"],
            username=key_owner
        )
    )

    # all errors will fail silently except for rate-limiting
    if r.status_code >= 400:
        if r.status_code == 403:
            global_keys.next()
            make_call(url)
        else:
            return None

    try:
        return r.json()
    except ValueError:
        return None


def get_profile(username, api_key_tuple):
    url = "https://api.github.com/users/{username}".format(
        username=username
    )
    return make_call(url, api_key_tuple)







def username_and_repo_name_from_github_url(url):
    try:
        path = urlparse(url).path
    except AttributeError:  # there's no url
        return [None, None]

    split_path = path.split("/")
    try:
        username = split_path[1]
    except IndexError:
        username = None

    try:
        repo_name = split_path[2]
    except IndexError:
        repo_name = None

    return [username, repo_name]