from datetime import timedelta
from os.path import realpath, dirname
import os

from flask import Response, render_template, abort, request
from . import *
from log import log
import json
from hackathon.functions import get_config
from login import login_providers
from flask_restful import Resource

Template_Routes = {
    "PrivacyStatement": "PrivacyStatement.html",
    "TermsOfUse": "TermsOfUse.html",
    'paper': "paper.html",
    "google": "google.html",
    "loading": "loading.html",
    "rightSide": "rightSide.html",
    "error": "error.html",
    "submitted": "submitted.html",
    "redirect": "redirect.html",
    "notregister": "notregister.html",
    "settings": "settings.html",
    "hackathon": "hackathon.html",
    "github": "github.html",
    "qq": "qq.html"
}


def simple_route(path):
    if Template_Routes.has_key(path):
        return render_template(Template_Routes[path])
    else:
        abort(404)


# index page
@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


# error handler for 404
@app.errorhandler(404)
def page_not_found(error):
    # render a beautiful 404 page
    log.error(error)
    return "Page not Found", 404


# error handler for 500
@app.errorhandler(500)
def internal_error(error):
    # render a beautiful 500 page
    log.error(error)
    return "Internal Server Error", 500


@app.route('/<path:path>')
def template_routes(path):
    return simple_route(path)


# js config
@app.route('/config.js')
def js_config():
    resp = Response(response="var CONFIG=%s" % json.dumps(get_config("javascript")),
                    status=200,
                    mimetype="application/javascript")
    return resp


class Get_login(Resource):
    def post(self):
        body = request.get_json()
        provider = body["provider"]
        return login_providers[provider].login(body)

api.add_resource(Get_login, "/ui/login")


# @app.route('/ui/login')


