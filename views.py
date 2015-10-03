from app import app

from models.search import autocomplete
from util import elapsed
from models.person import Person
from models import package
from models.package import Package
from models.package_jobs import get_leaders
from dummy_data import get_dummy_data
from sqlalchemy import orm
from models.package import make_host_name
from util import str_to_bool

from flask import make_response
from flask import request
from flask import abort
from flask import jsonify
from flask import render_template
from flask import redirect
from flask import url_for

from time import time

import os
import json


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
    if "localhost" in request.url or "dev.depsy.org" in request.url:
        # it's us, send the real one
        return render_template('index.html')
    else:

        # it's someone else, send a Coming Soon page.
        return render_template('coming-soon.html')















###########################################################################
# API
###########################################################################
@app.route("/api")
def api_test():
    return jsonify({"resp": "Hi, I'm Despy!"})

@app.route("/api/person/<person_id>")
@app.route("/api/person/<person_id>.json")
def person_endpoint(person_id):

    # data = get_dummy_data("person")
    # return json_resp_from_thing(data)

    from models.contribution import Contribution
    my_person = Person.query.options(orm.subqueryload_all(
            Person.contributions, 
            Contribution.package, 
            Package.contributions, 
            Contribution.person, 
            Person.contributions
        )).get(int(person_id))

    if not my_person:
        abort_json(404, "This person's not in the database")

    return json_resp_from_thing(my_person.to_dict())


@app.route("/api/package/<host_or_language>/<project_name>")
@app.route("/api/package/<host_or_language>/<project_name>.json")
def package_endpoint(host_or_language, project_name):


    my_id = package.make_id(host_or_language, project_name)

    from models.contribution import Contribution
    my_package = Package.query.options(
        orm.subqueryload_all(Package.contributions, Contribution.person)
    ).get(my_id)

    if not my_package:
        abort_json(404, "This package is not in the database")

    resp_dict = my_package.to_dict()
    return json_resp_from_thing(resp_dict)




@app.route("/api/packages")
@app.route("/api/packages.json")
def packages_endpoint():
    filters_dict = make_filters_dict(request.args)
    page_size = request.args.get("page_size", "25")

    start = time()
    packages = get_leaders(
        filters=filters_dict,
        page_size=int(page_size)
    )
    leaders_list = [p.as_snippet_with_people for p in packages]

    ret = json_resp_from_thing({
        "count": len(leaders_list),
        "list": leaders_list,
        "type": "package",
        "filters": filters_dict
    })

    elapsed_time = elapsed(start)
    ret.headers["x-elapsed"] = elapsed_time
    return ret

@app.route('/api/people')
def people_endpoint():
    pass

@app.route('/tags')
def tags_endpoint():
    pass

@app.route('/api/leaderboard')
@app.route('/api/leaderboard.json')
def leaders():
    filters_dict = make_filters_dict(request.args)
    page_size = request.args.get("page_size", "25")

    start = time()
    leaders = get_leaders(
        filters=filters_dict,
        page_size=int(page_size)
    )
    leaders_list = [leader.as_snippet for leader in leaders]

    ret = json_resp_from_thing({
        "count": len(leaders_list),
        "list": leaders_list,
        "type": filters_dict["type"],
        "filters": filters_dict
    })

    elapsed_time = elapsed(start)
    ret.headers["x-elapsed"] = elapsed_time
    return ret



@app.route("/api/search/<search_str>")
def search(search_str):
    ret = autocomplete(search_str)
    return jsonify({"list": ret, "count": len(ret)})


def make_filters_dict(args):
    full_dict = {
        "type": args.get("type", "package"),
        "is_academic": (args.get("is_academic", False)),
        "host": make_host_name(args.get("language", "python")),
        "tag": args.get("tag", None)
    }
    ret = {}

    # don't return keys with falsy values, we won't filter by them.
    for k, v in full_dict.iteritems():
        if v:
            ret[k] = v

    return ret





if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5008))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)





