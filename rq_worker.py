import optparse
import os
import sys
import logging
from rq import Worker
from rq import Queue
from rq import Connection
from rq.job import JobStatus
from app import redis_rq_conn




def failed_job_handler(job, exc_type, exc_value, traceback):

    print "RQ job failed! {}. here's more: {} {} {}".format(
        job.meta, exc_type, exc_value, traceback
    )
    return True  # job failed, drop to next level error handling




def start_worker(queue_name):
    print "starting worker {}...".format(queue_name)

    with Connection(redis_rq_conn):
        worker = Worker(Queue(queue_name), exc_handler=failed_job_handler)
        worker.work()


