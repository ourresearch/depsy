from app import app

from models.search import autocomplete
from util import elapsed
from models.person import Person
from models import package
from models.package import Package
from models.package_jobs import get_packages
from dummy_data import get_dummy_data
from sqlalchemy import orm

from flask import make_response
from flask import request
from flask import abort
from flask import jsonify
from flask import render_template

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
    return render_template('index.html')














###########################################################################
# API
###########################################################################
@app.route("/api")
def api_test():
    return jsonify({"resp": "Hi, I'm Impactstory!"})

@app.route("/api/person/<person_id>")
@app.route("/api/person/<person_id>.json")
def person_endpoint(person_id):

    # data = get_dummy_data("person")
    # return json_resp_from_thing(data)

    from models.contribution import Contribution
    my_person = Person.query.options(orm.subqueryload_all(Person.contributions, Contribution.package)).get(int(person_id))

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


@app.route("/api/package/<host_or_language>/<project_name>/rev-deps-tree")
@app.route("/api/package/<host_or_language>/<project_name>/rev-deps-tree.json")
def package_tree_endpoint(host_or_language, project_name):

    my_id = package.make_id(host_or_language, project_name)

    from models.contribution import Contribution
    my_package = Package.query.options(
        orm.subqueryload_all(Package.contributions, Contribution.person)
    ).get(my_id)

    if not my_package:
        abort_json(404, "This package is not in the database")

    resp_dict = my_package.tree
    return json_resp_from_thing(resp_dict)



@app.route("/api/packages")
@app.route("/api/packages.json")
def packages_endpoint():
    filter_strings = request.args.get("filters", "").split(",")
    filters = [s.split(":") for s in filter_strings if s]

    start = time()
    if type == "packages":
        packages = get_packages(filters)
        leaders_list = [p.as_snippet for p in packages]
    else:
        raise NotImplementedError("we can only rank packages right now...")

    ret = json_resp_from_thing({
        "list": leaders_list,
        "type": type,
        "filters": filters
    })

    elapsed_time = elapsed(start)
    ret.headers["x-elapsed"] = elapsed_time
    return ret



@app.route("/api/search/<search_str>")
def search(search_str):
    ret = autocomplete(search_str)
    return jsonify({"list": ret, "count": len(ret)})









if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5008))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)





