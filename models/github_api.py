import os
import logging
import requests
from urlparse import urlparse
import random
from app import db
from time import sleep
from time import time
from util import elapsed
import subprocess

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
            print "no good key found so double-checking expired keys"
            self.update_expired_keys()
            # try same thing again, once more...hopefully a key has un-expired.
            try:
                return self._get_good_key()
            except ValueError:  # no more tries for you.
                raise GithubRateLimitException


    def _get_good_key(self):
        tokens_str = os.environ["GITHUB_TOKENS"]
        keys = [t.split(":") for t in tokens_str.split(",")]

        good_keys = [k for k in keys if k not in self.expired_keys]

        # this throws a value error if no good keys
        ret_key = random.sample(good_keys, 1)[0]
        return ret_key

    def expire_key(self, login, token):
        print "expiring key:", login
        self.expired_keys.append([login, token])


    def update_expired_keys(self):
        rate_limit_check_url = "https://api.github.com/rate_limit"
        previously_expired_keys = self.expired_keys
        self.expired_keys = []
        for login, token in previously_expired_keys:
            print "calling rate limit check on ", loginy
            r = requests.get(rate_limit_check_url, auth=(login, token))
            remaining = r.json()["rate"]["remaining"]
            if remaining == 0:
                self.expired_keys.append([login, token])



# this needs to be a global that the whole application imports and uses
keyring = GithubKeyring()



def make_ratelimited_call(url, return_json=True, stream=False):

    try:
        login, token = keyring.get()
    except GithubRateLimitException:
        # wait a bit and try again, forever
        print "{}: our github keys have all reached their rate limits. sleeping....".format(
            url
        )
        sleep(5 * 60)
        print "make_ratelimited_call({}) trying again, mabye api keys refreshed?".format(url)
        return make_ratelimited_call(url)

    # assuming rate limited calls will never time out
    r = requests.get(url, auth=(login, token), stream=stream)

    try:
        calls_remaining = r.headers["X-RateLimit-Remaining"]
    except KeyError:
        calls_remaining = 9999999

    print "{status_code}: {url}.  {rate_limit} calls remain for {login}".format(
        status_code=r.status_code,
        url=url,
        rate_limit=calls_remaining,
        login=login
    )

    # deal w expired keys
    if int(calls_remaining) == 0:
        # this key is expired.

        keyring.expire_key(login, token)
        if r.status_code < 400:
            pass  # key just expired, but we got good data this call

        elif r.status_code == 403 or r.status_code == 401:
            # key is dead, and also we got no data. try again.
            print "error: got status_code", r.status_code
            return make_ratelimited_call(url)


    # return what we got
    if r.status_code >= 400:
        return {
            "error_code": r.status_code,
            "msg": r.text
        }
    else:
        try:
            if return_json:
                return r.json()
            else:
                return r
        except ValueError:
            return {
                "error_code": r.status_code,
                "msg": "no json in response"
            }


def get_repo_zip_response(login, repo_name):

    url = "https://api.github.com/repos/{login}/{repo_name}/zipball/master".format(
        login=login,
        repo_name=repo_name
    )
    return make_ratelimited_call(url, return_json=False, stream=True)






def get_profile(username, api_key_tuple):
    url = "https://api.github.com/users/{username}".format(
        username=username
    )
    return make_ratelimited_call(url, api_key_tuple)




def get_repo_data(login, repo_name, trim=True):
    trim_these_keys = [
        "owner",
        "organization",
        "parent",
        "source"
    ]

    url = "https://api.github.com/repos/{login}/{repo_name}".format(
        login=login,
        repo_name=repo_name
    )
    resp_dict = make_ratelimited_call(url)
    if trim:
        ret = {}
        for k, v in resp_dict.iteritems():
            if k in trim_these_keys or k.endswith("url"):
                pass  # this key not returned
            else:
                ret[k] = v
    else:
        ret = resp_dict

    return ret



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