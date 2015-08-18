"""
Downloads all the json metadata for each package on PyPi.

Uses several parts from https://gist.github.com/brettcannon/d03fbcf365a9c76d4aaa
You must run this file from
"""

import json
import os
import pickle
from xml import sax
from xml.sax import handler
from pathlib import Path
import requests



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
    return r.json()




def fetch_main(data_file_path):
    print('Fetching index ...')
    project_names_set = sorted(fetch_index())
    project_data = []

    print('Fetching {} projects ...').format(len(project_names_set))

    project_index = 1
    for project_name in project_names_set[0:10]:
        print "   {name} (#{index})".format(
            name=project_name,
            index=project_index
        )
        project = fetch_project(project_name)
        project["_name"] = project_name
        project_data.append(project)
        project_index += 1

    print "saving projects file to {}".format(data_file_path)
    with open(str(data_file_path), "w") as file:
        json.dump(project_data, file, indent=3, sort_keys=True)






if __name__ == '__main__':
    data_dir = Path(__file__, "../../data").resolve()
    data_file_path = Path(data_dir, "pypi_projects.json")
    fetch_main(data_file_path)