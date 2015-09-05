from time import time
from app import db
from util import elapsed




def make_update_fn(cls, method_name):
    def fn(obj_id):
        start_time = time()

        obj = db.session.query(cls).get(obj_id)
        if obj is None:
            return None

        method_to_run = getattr(obj, method_name)

        print u"running {repr}.{method_name}() method".format(
            repr=obj,
            method_name=method_name
        )

        method_to_run()
        db.session.commit()

        print u"finished {repr}.{method_name}(). took {elapsed}sec".format(
            repr=obj,
            method_name=method_name,
            elapsed=elapsed(start_time, 4)
        )
        return None  # important for if we use this on RQ

    return fn
