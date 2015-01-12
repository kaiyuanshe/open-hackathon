__author__ = "Junbo Wang"

import os
from os.path import realpath, dirname

from flask import request, render_template, g
from flask_restful import reqparse, abort, Resource

from hackathon.expr.expr_mgr import ExprManager
from database.models import Announcement
from ossdocker import *
from hackathon import user_manager, expr_manager


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
    "hackathon": "hackathon.html"
}

manager = ExprManager()


def simple_route(path):
    if Template_Routes.has_key(path):
        register = user_manager.get_registration_by_email(g.user.email)
        return render_template(Template_Routes[path], user=g.user, register=register)
    else:
        abort(404)


class CourseList(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('tag', default=None)
        args = parser.parse_args()


class StatusList(Resource):
    # =======================================================return data start
    # [{"register_name":"zhang", "online":"1","submitted":"0"..."description":" "}]
    # =======================================================return data end
    def get(self):
        json_ret = map(lambda u: u.json(), user_manager.get_all_registration())
        return json_ret

    # =======================================================test data start
    # {"id":1, "online":1,"submitted":0}
    # =======================================================test data end
    def put(self):
        args = request.get_json()
        return expr_manager.submit_expr((args))


class DoCourse(Resource):
    def get(self, id):
        cs = manager.get_expr_status(id)
        if cs is not None:
            return cs
        else:
            return "Not Found", 404

    def post(self, id):
        # the id is actually the name of template when POST
        template_file = "%s/resources/%s_docker.js" % (dirname(realpath(__file__)), id)
        if os.path.isfile(template_file):
            # call remote service to start docker containers
            expr_config = json.load(file(template_file))
            try:
                return manager.start_expr(expr_config)
            except Exception as err:
                log.error(err)
                return "fail to start due to '%s'" % err, 500
        else:
            return "the experiment %s is not ready" % id, 404

    def delete(self, id):
        return manager.stop_expr(id)

    def put(self, id):
        return manager.heart_beat(id)


class Anmt(Resource):
    def get(self):
        return Announcement.query.filter_by(enabled=1).first().json()