from time import time
from models.pypi_repo import save_all_repo_owners_and_key_committers
from app import db
import argparse
import logging


def test_no_args():
    print "test_no_args function ran"

def test_one_arg(one):
    print "test_one_arg function ran", one

def test_one_optional_arg(one=None):
    print "test_one_optional_arg function ran", one

def test_two_args(one, two=None):
    print "test_two_args function ran", one, two


def main(fn, optional_args=None):

    # call function by its name in this module, with all args :)
    # http://stackoverflow.com/a/4605/596939
    if optional_args:
        globals()[fn](*optional_args)
    else:
        globals()[fn]()


if __name__ == "__main__":

    db.create_all()

    # get args from the command line:
    parser = argparse.ArgumentParser(description="Run stuff.")
    parser.add_argument('function', type=str, help="what function you want to run")
    parser.add_argument('optional_args', nargs='*', help="positional args for the function")

    args = vars(parser.parse_args())

    function = args["function"]
    optional_args = args["optional_args"]

    print u"main.py {function} with {optional_args}".format(
        function=function.upper(), optional_args=optional_args)

    global logger
    logger = logging.getLogger("ti.main.{function}".format(
        function=function))

    main(function, optional_args)

    db.session.remove()


