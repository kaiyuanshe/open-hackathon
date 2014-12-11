__author__ = "Junbo Wang"

from flask import Flask, request, render_template, g ,session
from flask.ext.restful import reqparse, abort, Api, Resource
import json, time, os
from sample_course import Sample_Courses
from expr_mgr import ExprManager;
from os.path import realpath, dirname
from log import log
from registration import Registration

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
    "notregister": "notregister.html"
}

manager = ExprManager()

def simple_route(path):
    session.permanent = False
    if Template_Routes.has_key(path):
        return render_template(Template_Routes[path])
    else:
        abort(404)

class CourseList(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('tag', default=None)
        args = parser.parse_args()

        kw = args['tag']
        if kw is None:
            return json.dumps(Sample_Courses)
        else:
            ret = filter(lambda c: len(filter(lambda t: kw.lower() in t.lower(), c["tags"])) > 0, Sample_Courses)
            return json.dumps(ret)

class StatusList(Resource):
    # =======================================================return data start
    # [{"register_name":"zhang", "online":"1","submitted":"0"..."description":" "}]
    # =======================================================return data end
    def get(self):
        r = Registration()
        return json.dumps(r.get_all())

    # =======================================================test data start
    # {"id":1, "online":1,"submitted":0}
    # =======================================================test data end
    def put(self):
        args = request.get_json()
        r = Registration()
        return r.submit(args)


class DoCourse(Resource):
    def get(self, id):
        cs = manager.get_expr_status(id)
        if cs is not None:
            return cs
        else:
            return "Not Found", 404

    def post(self, id):
        # the id is actually the name of template when POST
        template_file= "%s/resources/%s_docker.js" % (dirname(realpath(__file__)), id)
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
