from app import app, db
from sqlalchemy import sql

from models.profile import Profile
from models.profile import create_profile
from models.repo import create_repo
from models.repo import Repo
from models.search import autocomplete

from models.person import Person
from models.package import Package
from dummy_data import get_dummy_data

from flask import make_response
from flask import request
from flask import abort
from flask import jsonify
from flask import g
from flask import render_template


import os
import json
from datetime import datetime
from datetime import timedelta
import jwt
from jwt import DecodeError
from jwt import ExpiredSignature
from functools import wraps




import requests
from urlparse import parse_qsl

import logging

logger = logging.getLogger("views")



def json_dumper(obj):
    """
    if the obj has a to_dict() function we've implemented, uses it to get dict.
    from http://stackoverflow.com/a/28174796
    """
    try:
        return obj.to_dict()
    except AttributeError:
        return obj.__dict__


def json_resp_from_thing(thing):
    hide_keys = request.args.get("hide", "").split(",")
    if hide_keys is not None:
        for key_to_hide in hide_keys:
            try:
                del thing[key_to_hide]
            except KeyError:
                pass

    json_str = json.dumps(thing, sort_keys=True, default=json_dumper, indent=4)

    if request.path.endswith(".json") and (os.getenv("FLASK_DEBUG", False) == "True"):
        logger.info(u"rendering output through debug_api.html template")
        resp = make_response(render_template(
            'debug_api.html',
            data=json_str))
        resp.mimetype = "text/html"
    else:
        resp = make_response(json_str, 200)
        resp.mimetype = "application/json"
    return resp


def abort_json(status_code, msg):
    body_dict = {
        "HTTP_status_code": status_code,
        "message": msg,
        "error": True
    }
    resp_string = json.dumps(body_dict, sort_keys=True, indent=4)
    resp = make_response(resp_string, status_code)
    resp.mimetype = "application/json"
    abort(resp)


@app.route("/<path:page>")  # from http://stackoverflow.com/a/14023930/226013
@app.route("/")
def index_view(path="index", page=""):
    return render_template('index.html')











###########################################################################
# from satellizer.
# move to another file later
###########################################################################

def create_token(profile):
    return create_token_from_username(profile.username)

def create_token_from_username(username):  # j added this one.
    payload = {
        'sub': username,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=14)
    }
    key = app.config['SECRET_KEY']
    logger.info('creating a token using this username: ' + username)
    token = jwt.encode(payload, key)
    return token.decode('unicode_escape')


def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, app.config['SECRET_KEY'])


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response

        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        g.current_user_username = payload['sub']

        return f(*args, **kwargs)

    return decorated_function





###########################################################################
# API
###########################################################################
@app.route("/api")
def api_test():
    return jsonify({"resp": "Hi, I'm Impactstory!"})

@app.route("/api/person/<person_id>")
@app.route("/api/person/<person_id>.json")
def person_endpoint(person_id):

    #data = get_dummy_data("person")
    #return json_resp_from_thing(data)

    person = Person.query.get(int(person_id))

    if not person:
        abort_json(404, "This person's not in the database")

    return json_resp_from_thing(person.to_dict())


@app.route("/api/p/<host>/<project_name>")
@app.route("/api/p/<host>/<project_name>.json")
def package(host, project_name):

    if host.lower() == "python":
        id = "pypi:" + project_name
    elif host.lower() == "r":
        id = "cran:" + project_name

    my_package = Package.query.get(id)

    if not my_package:
        abort_json(404, "This person's not in the database")

    resp_dict = my_package.to_dict()
    return json_resp_from_thing(resp_dict)






@app.route("/api/search/<search_str>")
def search(search_str):
    ret = autocomplete(search_str)
    return jsonify({"list": ret, "count": len(ret)})









if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5008))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)





