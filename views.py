from app import app, db
from providers import github
from models.profile import Profile
from models.profile import create_profile
from models.repo import create_repo
from models.repo import Repo

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
    logger.info('creating a token using this payload: ' + json.dumps(payload))
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

@app.route("/api/u/<username>")
@app.route("/api/u/<username>.json")
def api_users(username):
    profile = None
    profile = Profile.query.get(username)

    if not profile:
        profile = create_profile(username)
    return json_resp_from_thing(profile.to_dict())

@app.route('/api/me')
@login_required
def me():
    profile = Profile.query.get(g.current_user_username)
    return json_resp_from_thing(profile.to_dict())


@app.route("/api/r/<username>/<reponame>")
@app.route("/api/r/<username>/<reponame>.json")
def api_repo(username, reponame):
    repo = None

    # Comment this next line out for debugging,
    # it makes a new profile every time.
    repo = Repo.query.filter(Repo.username==username, Repo.reponame==reponame).first()

    if not repo:
        repo = create_repo(username, reponame)
    return json_resp_from_thing( repo.display_dict())



@app.route('/auth/github', methods=['POST'])
def github():
    """
    based on satellizer example here:
    https://github.com/sahat/satellizer/blob/master/examples/server/python/app.py#L199
    """

    logger.info(u"in /auth/github")

    access_token_url = 'https://github.com/login/oauth/access_token'
    users_api_url = 'https://api.github.com/user'

    params = {
        'client_id': request.json['clientId'],
        'redirect_uri': request.json['redirectUri'],
        'client_secret': app.config['GITHUB_SECRET'],
        'code': request.json['code']
    }

    # Step 1. Exchange authorization code for access token.
    r = requests.get(access_token_url, params=params)
    access_token = dict(parse_qsl(r.text))
    headers = {'User-Agent': 'Impactstory'}

    # Step 2. Retrieve information about the current user.
    r = requests.get(users_api_url, params=access_token, headers=headers)
    github_profile = json.loads(r.text)
    logger.info(u"we got a profile back from github." + ",".join(github_profile.keys()))


    # Step 3. (optional) Link accounts. REMOVED, we don't need this. since we're
    # only using public stuff, this authentication doesnt' actually give us
    # any new information if we have the profile

    # Step 4. Create a new account or return an existing one. REMOVED, because
    # simply hitting /api/u/:username creates the profile, this is just for
    # logging in.
    # that means just hitting this endpoint WON'T create a profile, someone
    # (the client) needs you to hit /api/u/:username for that to happen.

    # return the token. used to be part of their Step 4, but j extracted it.
    github_username = github_profile['login']
    token = create_token_from_username(github_username)
    logger.info("trying to jsonify this token", token)
    return jsonify(token)





if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5008))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
