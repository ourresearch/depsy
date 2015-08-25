import os
import logging
import requests
from urlparse import urlparse
import random
from app import db


logger = logging.getLogger("github_api")

class GithubRateLimitException(Exception):
    pass

class GithubKeyring():
    def __init__(self):
        self.expired_keys = []

    def get(self):
        """
        get a key. if there is no key, try to see if one is un-expired

        if this raises the GithubRateLimitException,
        you should a lil while before re-calling this, it will hit the
         network a lot if none of the keys are un-expired
        """
        try:
            return self._get_good_key()
        except ValueError:
            self.update_expired_keys()
            # try same thing again, once more...hopefully a key has un-expired.
            try:
                return self._get_good_key()
            except ValueError:  # no more tries for you.
                raise GithubRateLimitException


    def _get_good_key(self):
        tokens_str = os.environ["GITHUB_TOKENS"]
        keys  = [t.split(":") for t in tokens_str.split(",")]
        good_keys = [k for k in keys if k not in self.expired_keys]

        # this throws a value error if no good keys
        ret_key = random.sample(good_keys, 1)
        return ret_key

    def expire_key(self, login, token):
        self.expired_keys.append([login, token])


    def update_expired_keys(self):
        rate_limit_check_url = "https://api.github.com/rate_limit"
        self.expired_keys = []
        for login, token in self.expired_keys:
            r = requests.get(rate_limit_check_url, auth=(login, token))
            remaining = r.json()["rate"]["remaining"]
            if remaining == 0:
                self.expired_keys.append([login, token])

        return True


# this needs to be a global that the whole application imports and uses
keyring = GithubKeyring()



def make_call(url):

    try:
        key_owner, key_token = global_keys.get()
    except TypeError:  # there are no more keys.
        raise GithubRateLimitException


    r = requests.get(url, auth=(key_owner, key_token))
    calls_remaining = r.headers["X-RateLimit-Remaining"]

    logger.info(
        "{status_code}: {url}.  {rate_limit} calls remain for {username}".format(
            status_code=r.status_code,
            url=url,
            rate_limit=calls_remaining,
            username=key_owner
        )
    )

    if int(calls_remaining) == 0:
        global_keys.next()
        return make_call(url)

    # all errors will fail silently except for rate-limiting (caught above)
    if r.status_code >= 400:
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