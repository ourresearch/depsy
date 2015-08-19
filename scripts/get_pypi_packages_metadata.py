"""
Downloads all the json metadata for each package on PyPi.

Uses several parts from https://gist.github.com/brettcannon/d03fbcf365a9c76d4aaa
You must run this file from
"""

import json
from concurrent import futures
from xml import sax
from xml.sax import handler
from pathlib import Path
import requests
import time



class PyPiException(Exception):
    pass


class PyPIIndexHandler(handler.ContentHandler):

    """Parse PyPI's simple index page."""

    def __init__(self):
        handler.ContentHandler.__init__(self)
        self.projects = set()

    def startElement(self, name, attrs):
        # TODO: Check for <meta name="api-version" value="2" /> .
        if name != 'a':
            return

        project_name = attrs.get('href', None)
        if project_name is not None:
            self.projects.add(project_name)


def fetch_index():
    """Return an iterable of every project name on PyPI."""

    r = requests.get('https://pypi.python.org/simple/')
    sax_handler = PyPIIndexHandler()
    sax.parseString(r.text, sax_handler)
    return sax_handler.projects


def fetch_project(name):
    """Return the loaded JSON data from PyPI for a project."""
    url = 'https://pypi.python.org/pypi/{}/json'.format(name)
    r = requests.get(url)
    try:
        return r.json()
    except ValueError:
        # has to *return* an error instead of raising one,
        # cos there seems to be no way to handle errors from here in
        # ThreadPoolExecutor.map()
        return PyPiException("error on package'{}'".format(name))




def fetch_main(data_file_path):
    start_time = time.time()
    print('Fetching index ...')
    project_names_set = sorted(fetch_index())
    project_data = []
    errors = []

    print('Fetching {} projects ...').format(len(project_names_set))


    with futures.ThreadPoolExecutor(10) as executor:
        for data in executor.map(fetch_project, project_names_set):
            if isinstance(data, PyPiException):
                print "   *** ERROR: {} ***".format(data)
                errors.append(str(data))

            else:
                project_data.append(data)
                print "   {} ".format(data["info"]["name"])


    print "finished getting data in {} seconds".format(
        round(time.time() - start_time, 2)
    )
    print "saving projects file to {}".format(data_file_path)
    with open(str(data_file_path), "w") as file:
        json.dump(project_data, file, indent=3, sort_keys=True)

    print "got these errors:"
    for msg in errors:
        print "  " + msg






if __name__ == '__main__':
    data_dir = Path(__file__, "../../data").resolve()
    data_file_path = Path(data_dir, "pypi_projects.json")
    fetch_main(data_file_path)