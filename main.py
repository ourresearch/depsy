from time import time
from models.pypi_repo import save_all_repo_owners_and_key_committers
from app import db
import argparse
import logging



def test():
    print "test function ran"

def main(fn, args):
    # call function by its name in this module, with all args :)
    # http://stackoverflow.com/a/4605/596939
    if args:
        globals()[fn](args)
    else:
        globals()[fn](**args.split(","))


if __name__ == "__main__":

    db.create_all()

    # get args from the command line:
    parser = argparse.ArgumentParser(description="Run stuff.")
    parser.add_argument('function', type=str, help="what function you want to run")
    parser.add_argument('--args', default=None, type=str, help="optional args to pass to function")

    args = vars(parser.parse_args())
    function = args["function"]

    arg_string = dict((k, v) for (k, v) in args.iteritems() if v and k!="function")
    print u"main.py {function} with {arg_string}".format(
        function=function.upper(), arg_string=arg_string)

    global logger
    logger = logging.getLogger("ti.daily.{function}".format(
        function=function))

    main(function, args)

    db.session.remove()