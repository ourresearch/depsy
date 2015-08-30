import os
import logging
import requests
from urlparse import urlparse
import random
from time import sleep
from time import time
from util import elapsed
import json
import subprocess32
import base64
import re
import ast

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

    def update_expired_keys(self):
        previously_expired_keys = self.expired_keys
        self.expired_keys = []
        for login, token in previously_expired_keys:
            remaining = self._check_remaining_for_key(login, token)
            if remaining == 0:
                self.expired_keys.append([login, token])

    def expire_key(self, login, token):
        print "expiring key:", login
        self.expired_keys.append([login, token])

    def report(self):
        print "remaining calls by key: "
        total_remaining = 0
        for login, token in self._keys_from_env():
            remaining = self._check_remaining_for_key(login, token)
            total_remaining += remaining
            print "{login:>16}: {remaining}".format(
                login=login,
                remaining=remaining
            )

        print "{:>16}: {}".format(
            "TOTAL",
            total_remaining
        )
        print "\n"

    def _get_good_key(self):
        good_keys = [k for k in self._keys_from_env() if k not in self.expired_keys]

        # this throws a value error if no good keys
        ret_key = random.sample(good_keys, 1)[0]
        return ret_key


    def _check_remaining_for_key(self, login, token):
        url = "https://api.github.com/rate_limit"
        r = requests.get(url, auth=(login, token))
        return r.json()["rate"]["remaining"]

    def _keys_from_env(self):
        tokens_str = os.environ["GITHUB_TOKENS"]
        return [t.split(":") for t in tokens_str.split(",")]





# this needs to be a global that the whole application imports and uses
keyring = GithubKeyring()


class ZipGetterException(Exception):
    db_str = None

class NotFoundException(Exception):
    pass

class ZipGetter():

    def __init__(self, url, login=None, token=None):
        self.url = url
        self.login = login
        self.token = token
        self.download_elapsed = 0
        self.grep_elapsed = 0
        self.download_kb = 0
        self.error = None
        self.temp_file_name = "GithubRepoZip.temp.zip"
        self.dep_lines = None


    def download(self):
        # this is a cleaner way to handle errors, but not done yet...
        try:
            return self._download()
        except ZipGetterException:
            # do more stuff here
            print "zip getter exception"

    def _download(self):

        # @todo erase the temp file when something goes wrong...

        start = time()
        if self.login and self.token:
            print "Downloading zip from {} with HTTP basic auth {}:{}...".format(
                self.url,
                self.login,
                self.token
            )
            r = requests.get(self.url, stream=True, auth=(self.login, self.token))
        else:
            print "Downloading zip from {}...".format(self.url)
            r = requests.get(self.url, stream=True)

        if r.status_code == 400:
            print "DOWNLOAD ERROR for {}: file not found".format(r.url)
            self.error = "request_error_400"
            return None
        elif r.status_code > 400:
            print "DOWNLOAD ERROR for {}: {} ({})".format(r.url, r.status_code, r.reason)
            self.error = "request_error"
            return None

        with open(self.temp_file_name, 'wb') as out_file:
            r.raw.decode_content = False

            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    out_file.write(chunk)
                    out_file.flush()
                    self.download_kb += 1
                    self.download_elapsed = elapsed(start, 4)
                    if self.download_kb > 256*1024:
                        print "DOWNLOAD ERROR for {}: file too big".format(self.url)
                        self.error = "file_too_big"
                        return None

                    if self.download_elapsed > 60:
                        print "DOWNLOAD ERROR for {}: taking too long".format(self.url)
                        self.error = "file_too_slow"
                        return None

        self.download_elapsed = elapsed(start, 4)
        print "downloaded {} ({}kb) in {} sec".format(
            self.url,
            self.download_kb,
            self.download_elapsed
        )


    def _grep_for_dep_lines(self, query_str, include_globs, exclude_globs):
        arg_list =['zipgrep', query_str, self.temp_file_name]
        arg_list += include_globs
        arg_list.append("-x")
        arg_list += exclude_globs
        start = time()

        try:
            print "Running zipgrep: '{}'".format(" ".join(arg_list))
            self.dep_lines = subprocess32.check_output(
                arg_list,
                timeout=90
            )

        except subprocess32.CalledProcessError:
            # heroku throws an error here when there are no dep lines to find.
            # but it's fine. there just aren't no lines.
            pass

        except subprocess32.TimeoutExpired:
            # too many files, we'll skip it and move on.
            self.error = "grep_timeout"
            pass

        finally:
            self.grep_elapsed = elapsed(start, 4)
            #print "found these dep lines: {}".format(self.dep_lines)
            print "finished dep lines search in {} sec".format(self.grep_elapsed)


    def get_dep_lines(self, language):
        self.download()
        if self.error:
            print "There are problems with the downloaded zip, quitting without getting deps."
            return None

        if language == "r":
            print "getting dep lines in r"
            include_globs = []
            query_str = "library|require"
            r_include_globs = ["*.R", "*.Rnw", "*.Rmd", "*.Rhtml", "*.Rtex", "*.Rst"]
            for r_include_glob in r_include_globs:
                include_globs.append(r_include_glob.upper())
                include_globs.append(r_include_glob.lower())

            include_globs += r_include_globs

            exclude_globs = ["*.foo"]  # hack, because some value is expected
            self._grep_for_dep_lines(query_str, include_globs, exclude_globs)

        elif language == "python":
            print "getting dep lines in python"
            query_str = "import"
            include_globs = ["*.py", "*.ipynb"]
            exclude_globs = ["*/venv/*", "*/virtualenv/*", "*/bin/*", "*/lib/*", "*/Lib/*", "*/library/*", "*/vendor/*"]
            self._grep_for_dep_lines(query_str, include_globs, exclude_globs)



def github_zip_getter_factory(login, repo_name):
    url = "https://codeload.github.com/{login}/{repo_name}/legacy.zip/master".format(
        login=login,
        repo_name=repo_name
    )
    getter = ZipGetter(url)
    return getter

    #url = "https://api.github.com/repos/{login}/{repo_name}/zipball/master".format(
    #    login=login,
    #    repo_name=repo_name
    #)
    #login, token = keyring.get()
    #getter = ZipGetter(url, login, token)
    #return getter




def make_ratelimited_call(url):

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
    r = requests.get(url, auth=(login, token))

    calls_remaining = r.headers["X-RateLimit-Remaining"]

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
            return r.json()
        except ValueError:
            return {
                "error_code": r.status_code,
                "msg": "no json in response"
            }




def get_profile(username, api_key_tuple):
    url = "https://api.github.com/users/{username}".format(
        username=username
    )
    return make_ratelimited_call(url, api_key_tuple)


def get_python_requirements(login, repo_name):
    try:
        ret = get_requirements_txt_requirements(login, repo_name)
        print "got {} requirements.txt requirements for {}/{}".format(
            len(ret),
            login,
            repo_name
        )
    except NotFoundException:
        ret = get_setup_py_requirements(login, repo_name)
        print "got {} setup.py requirements for {}/{}".format(
            len(ret),
            login,
            repo_name
        )
    return sorted(ret)



def get_setup_py_requirements(login, repo_name):
    url = 'https://api.github.com/repos/{login}/{repo_name}/contents/setup.py'.format(
        login=login,
        repo_name=repo_name
    )
    resp = make_ratelimited_call(url)
    try:
        file_contents = resp["content"]
    except KeyError:
        raise NotFoundException

    decoded_file_contents = base64.decodestring(file_contents)
    parsed = ast.parse(decoded_file_contents)
    ret = []
    # see ast docs: https://greentreesnakes.readthedocs.org/en/latest/index.html
    for node in ast.walk(parsed):
        try:
            if node.func.id == "setup":
                for keyword in node.keywords:
                    if keyword.arg=="install_requires":
                        for elt in keyword.value.elts:
                            ret.append(elt.s)
                    if keyword.arg == "extras_require":
                        for my_list in keyword.value.values:
                            for elt in my_list.elts:
                                ret.append(elt.s)

        except AttributeError:
            continue

    return ret


def get_requirements_txt_requirements(login, repo_name):
    url = 'https://api.github.com/repos/{login}/{repo_name}/contents/requirements.txt'.format(
        login=login,
        repo_name=repo_name
    )
    resp = make_ratelimited_call(url)
    try:
        file_contents = resp["content"]
    except KeyError:
        raise NotFoundException

    # see here for spec used in parsing the file:
    # https://pip.readthedocs.org/en/1.1/requirements.html#the-requirements-file-format
    # it doesn't mention the '#' comment but found it often in examples.
    # not using this test str in  the function, just a handy place to keep it.
    test_str = """# my comment
file://blahblah
-e http:blahblah
foo==10.2
baz>=3.6
foo.bar>=3.33
foo-bar==2.2
foo_bar==1.1
foo == 5.5
-e http://blah
  foo_with_space_in_front = 1.1"""

    decoded_file_contents = base64.decodestring(file_contents)
    reqs = re.findall(
        r'^(?!#|file|-e)\s*([\w\.-]+)',
        decoded_file_contents,
        re.MULTILINE | re.IGNORECASE
    )
    return reqs




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




def get_github_homepage(url):
    try:
        parsed = urlparse(url)
    except AttributeError:
        return None  # no url was given

    # we are getting rid of things that
    # 1. aren't on github (duh)
    # 2. are just "github.com"
    # this leaves some things that have multiple pypi project in one github repo
    if parsed.netloc == "github.com" and len(parsed.path.split("/")) > 1:
        return url
    else:
        return None


def check_keys():
    keyring.report()




"""useful sql for checking speed of things going into the database"""
# update github_repo set dependency_lines=null where dependency_lines is not null;
# update github_repo set zip_download_elapsed=null where zip_download_elapsed is not null;
# update github_repo set zip_grep_elapsed=null where zip_grep_elapsed is not null;
# update github_repo set zip_download_size=null where zip_download_size is not null;
# update github_repo set zip_download_error=null where zip_download_error is not null;

# select count(*) as count_rows,
#     sum(zip_download_elapsed) as download, 
#     sum(zip_grep_elapsed) as grep, 
#     sum(zip_download_elapsed) + sum(zip_grep_elapsed) as total,
#     (sum(zip_download_elapsed) + sum(zip_grep_elapsed)) / count(*) as seconds_per_row
#     from github_repo
#     where zip_download_elapsed is not null
    
# select login, repo_name, zip_download_elapsed, zip_grep_elapsed, zip_download_elapsed+zip_grep_elapsed as total, zip_download_size
# from github_repo
# where zip_download_elapsed is not null
# order by login, repo_name









