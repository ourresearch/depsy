from time import time
from time import sleep
from app import db
from util import elapsed
from app import ti_queues
from sqlalchemy.dialects import postgresql



def make_update_fn(cls, method_name, commit=True):
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
        if commit:  # you can pass commit=False when you're testing stuff.
            db.session.commit()

        print u"finished {repr}.{method_name}(). took {elapsed}sec".format(
            repr=obj,
            method_name=method_name,
            elapsed=elapsed(start_time, 4)
        )
        return None  # important for if we use this on RQ

    return fn


def enqueue_jobs(q, fn, queue_number, *args):
    """
    Takes sqlalchemy query with (login, repo_name) IDs, runs fn on those repos.
    """
    empty_queue(queue_number)

    print "running eneueueue jobs, here are the args", q, fn, queue_number
    print "running fn()"
    fn()
    print "ran fn()"

    start_time = time()
    new_loop_start_time = time()
    index = 0

    print "running this query: \n{}\n".format(
        q.statement.compile(dialect=postgresql.dialect())
    )
    row_list = q.all()
    num_jobs = len(row_list)
    print "finished query in {}sec".format(elapsed(start_time))
    print "adding {} jobs to queue...".format(num_jobs)

    for object_id_row in row_list:
        row_args = list(object_id_row)
        row_args += args  # pass incoming option args to the enqueued function

        job = ti_queues[queue_number].enqueue_call(
            func=fn,
            args=row_args,
            result_ttl=0  # number of seconds
        )
        job.meta["object_id"] = list(object_id_row)
        job.save()
        if index % 1000 == 0:
            print "added {} jobs to queue in {}sec total, {}sec this loop".format(
                index,
                elapsed(start_time),
                elapsed(new_loop_start_time)
            )
            new_loop_start_time = time()
        index += 1
    print "last object added to the queue was {}".format(list(object_id_row))

    monitor_queue(queue_number, start_time, num_jobs)
    return True


def monitor_queue(queue_number, start_time, num_jobs):
    current_count = ti_queues[queue_number].count
    time_per_job = 1
    while current_count:
        sleep(1)
        current_count = ti_queues[queue_number].count
        done = num_jobs - current_count
        try:
            time_per_job = elapsed(start_time) / done
        except ZeroDivisionError:
            pass

        mins_left = int(current_count * time_per_job / 60)

        print "finished {done} jobs in {elapsed} min. {left} left (est {mins_left}min)".format(
            done=done,
            elapsed=int(elapsed(start_time) / 60),
            mins_left=mins_left,
            left=current_count
        )
    print "Done! {} jobs took {} seconds (avg {} secs/job)".format(
        num_jobs,
        elapsed(start_time),
        time_per_job
    )
    return True


def empty_queue(queue_number):
    num_jobs = ti_queues[queue_number].count
    ti_queues[queue_number].empty()

    print "emptied {} jobs on queue #{}....".format(
        num_jobs,
        queue_number
    )

