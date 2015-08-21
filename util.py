import time
from app import db

def dict_from_dir(obj, keys_to_ignore=None, keys_to_show="all"):

    if keys_to_ignore is None:
        keys_to_ignore = []
    elif isinstance(keys_to_ignore, basestring):
        keys_to_ignore = [keys_to_ignore]

    ret = {}

    if keys_to_show != "all":
        for key in keys_to_show:
            ret[key] = getattr(obj, key)

        return ret


    for k in dir(obj):
        value = getattr(obj, k)

        if k.startswith("_"):
            pass
        elif k in keys_to_ignore:
            pass
        # hide sqlalchemy stuff
        elif k in ["query", "query_class", "metadata"]:
            pass
        elif callable(value):
            pass
        else:
            try:
                # convert datetime objects...generally this will fail becase
                # most things aren't datetime object.
                ret[k] = time.mktime(value.timetuple())
            except AttributeError:
                ret[k] = value
    return ret


def median(my_list):
    """
    Find the median of a list of ints

    from https://stackoverflow.com/questions/24101524/finding-median-of-list-in-python/24101655#comment37177662_24101655
    """
    my_list = sorted(my_list)
    if len(my_list) < 1:
            return None
    if len(my_list) %2 == 1:
            return my_list[((len(my_list)+1)/2)-1]
    if len(my_list) %2 == 0:
            return float(sum(my_list[(len(my_list)/2)-1:(len(my_list)/2)+1]))/2.0


def underscore_to_camelcase(value):
    words = value.split("_")
    capitalized_words = []
    for word in words:
        capitalized_words.append(word.capitalize())

    return "".join(capitalized_words)



def page_query(q, page_size=1000):
    offset = 0
    while True:
        r = False
        print "util.page_query() retrieved {} things".format(page_query())
        for elem in q.limit(page_size).offset(offset):
            r = True
            yield elem
        offset += page_size
        if not r:
            break

def elapsed(since):
    return round(time.time() - since, 2)

def update_sqla_objects(sqla_objects, fn):
    flush_size = 10
    index = 1
    start = time.time()
    print "updating {} sqla_objects...".format(len(sqla_objects))
    for sqla_object in sqla_objects:
        fn(sqla_object)
        #db.session.merge(sqla_object)
        index += 1
        if index % flush_size == 0:
            db.session.commit()
            print "committed {index} objects in {sec} sec".format(
                index=index,
                sec=elapsed(start)
            )

    print "commiting objects..."
    db.session.commit()
    print "finished update in {} sec.".format(elapsed(start))


def get_sqla_objects(q):
    start = time.time()
    index = 1

    print "getting sqla objects..."
    ret = []
    for sqla_obj in page_query(q):
        ret.append(sqla_obj)
        if index % 1000 == 0:
            print "got {num} objects down in {secs}.".format(
                num=index,
                secs=elapsed(start)
            )

    return ret






