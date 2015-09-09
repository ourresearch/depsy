import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

import redis
from rq import Queue

import os
import logging
import sys


# set up logging
# see http://wiki.pylonshq.com/display/pylonscookbook/Alternative+logging+configuration
logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,
    format='%(name)s - %(message)s'
)
logger = logging.getLogger("software")

libraries_to_mum = [
    "requests.packages.urllib3",
    "stripe",
    "oauthlib",
    "boto",
    "newrelic",
    "RateLimiter"
]

for a_library in libraries_to_mum:
    the_logger = logging.getLogger(a_library)
    the_logger.setLevel(logging.WARNING)
    the_logger.propagate = True



app = Flask(__name__)
app.debug = True

# database stuff
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_POOL_SIZE"] = 60
app.config['GITHUB_SECRET'] = os.getenv("GITHUB_SECRET")

my_redis = redis.from_url(
    os.getenv("REDIS_URL", "redis://127.0.0.1:6379"),
    db=10
)

redis_rq_conn = redis.from_url(
    os.getenv("REDIS_URL", "redis://127.0.0.1:6379"),
    db=0
)
# database stuff
db = SQLAlchemy(app)





# try from http://docs.sqlalchemy.org/en/latest/core/pooling.html#using-connection-pools-with-multiprocessing
from sqlalchemy import event
from sqlalchemy import exc
import os
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    connection_record.info['pid'] = os.getpid()

@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    pid = os.getpid()
    if connection_record.info['pid'] != pid:
        connection_record.connection = connection_proxy.connection = None
        raise exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" %
                (connection_record.info['pid'], pid)
        )





ti_queues = []
for i in range(0, 10):
    ti_queues.append(
        Queue("ti-queue-{}".format(i), connection=redis_rq_conn)
    )


# these imports are needed so that tables will get auto-created.
from models import github_repo
from models import profile
from models import repo
from models import github_user
#from models import pypi_project
from models import cran_project
from models import person
from models import contribution

db.create_all()
db.session.commit()



# from http://docs.sqlalchemy.org/en/latest/core/pooling.html
# This recipe will ensure that a new Connection will succeed even if connections in the pool 
# have gone stale, provided that the database server is actually running. 
# The expense is that of an additional execution performed per checkout
@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()






