from time import time
from app import db
import argparse
from jobs import update_registry
from util import elapsed

from models import package_jobs


"""
examples of calling this:

# update everything
python update.py Package.test --limit 10 --chunk 5

# update one thing
python update.py Package.test --id cran:BioGeoBEARS

"""



def parse_update_optional_args(parser):
    # just for updating lots
    parser.add_argument('--limit', "-l", nargs="?", type=int, help="how many jobs to do")
    parser.add_argument('--chunk', "-ch", nargs="?", type=int, help="how many to take off db at once")
    parser.add_argument('--after', nargs="?", type=str, help="minimum id or id start, ie 0000-0001")
    parser.add_argument('--rq', action="store_true", default=False, help="do jobs in this thread")

    # just for updating one
    parser.add_argument('--id', nargs="?", type=str, help="id of the one thing you want to update")
    parser.add_argument('--orcid', nargs="?", type=str, help="orcid id of the one thing you want to update")

    # parse and run
    parsed_args = parser.parse_args()
    return parsed_args


def run_update(parsed_args):
    update = update_registry.get(parsed_args.fn)

    start = time()

    #convenience method for handling an orcid
    if parsed_args.orcid:
        from models.person import Person
        my_person = db.session.query(Person).filter(Person.orcid_id==parsed_args.orcid).first()
        parsed_args.id = my_person.id

    update.run(
        use_rq=parsed_args.rq,
        obj_id=parsed_args.id,  # is empty unless updating just one row
        min_id=parsed_args.after,  # is empty unless minimum id
        num_jobs=parsed_args.limit,
        chunk_size=parsed_args.chunk
    )

    db.session.remove()
    print "finished update in {}sec".format(elapsed(start))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run stuff.")
    # for everything
    parser.add_argument('fn', type=str, help="what function you want to run")
    parsed_args = parse_update_optional_args(parser)
    run_update(parsed_args)



