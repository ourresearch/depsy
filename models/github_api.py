import os
import logging
import requests
from urlparse import urlparse


logger = logging.getLogger("github_api")


def get_api_keys():
    tokens_str = os.environ["GITHUB_TOKENS"]
    token_pairs = [t.split(":") for t in tokens_str.split(",")]
    return token_pairs


class GithubRateLimitException(Exception):
    pass


class GithubApi():
    def __init__(self, token_pair):
        self.auth_username = token_pair[0]
        self.auth_password = token_pair[1]

    def make_call(self, url):
        r = requests.get(url, auth=(self.auth_username, self.auth_password))

        logger.info(
            "{status_code}: {url}.  {rate_limit} calls remain for {username}".format(
                status_code=r.status_code,
                url=url,
                rate_limit=r.headers["X-RateLimit-Remaining"],
                username=self.auth_username
            )
        )

        # all errors will fail silently except for rate-limiting
        if r.status_code >= 400:
            if r.status_code == 403:
                raise GithubRateLimitException
            else:
                return None

        return r.json()


    def get_profile(self, username):
        url = "https://api.github.com/users/{username}".format(
            username=username
        )
        return self.make_call(url)

    def get_repo_contribs(self, username, repo_name):
        url = "https://api.github.com/repos/{username}/{repo_name}/contributors".format(
            username=username,
            repo_name=repo_name
        )
        return self.make_call(url)

    def get_repo_contribs_dict(self, username, repo_name):
        contribs_list = self.get_repo_contribs(username, repo_name)
        ret = {}
        for contrib_dict in contribs_list:
            ret[contrib_dict["login"]] = contrib_dict["contributions"]
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