from os.path import realpath, dirname
import os
from flask_restful import Resource, reqparse
from . import api
from expr import expr_manager
from database.models import Announcement
from user.login import *
from flask import g, request
from log import log
from database import db_adapter
from decorators import token_required


class StatusList(Resource):
    # =======================================================return data start
    # [{"register_name":"zhang", "online":"1","submitted":"0"..."description":" "}]
    # =======================================================return data end
    @token_required
    def get(self):
        json_ret = map(lambda u: u.json(), user_manager.get_all_registration())
        return json_ret

    # =======================================================test data start
    # {"id":1, "online":1,"submitted":0}
    # =======================================================test data end
    def put(self):
        args = request.get_json()
        return expr_manager.submit_expr(args)


class DoCourse(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        args = parser.parse_args()
        if 'id' not in args:
            return "Bad Request", 400

        cs = expr_manager.get_expr_status(args['id'])
        if cs is not None:
            return cs
        else:
            return "Not Found", 404

    @token_required
    def post(self):
        args = request.get_json()
        if "cid" not in args or "hackathon" not in args:
            return "invalid parameter", 400
        cid = args["cid"]
        hackathon = args["hackathon"]
        template_file = "%s/resources/%s-%s.js" % (dirname(realpath(__file__)), hackathon, cid)
        if os.path.isfile(template_file):
            # call remote service to start docker containers
            expr_config = json.load(file(template_file))
            try:
                return expr_manager.start_expr(hackathon, expr_config)
            except Exception as err:
                log.error(err)
                return "fail to start due to '%s'" % err, 500
        else:
            return "the experiment %s is not ready" % id, 404

    @token_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int)
        args = parser.parse_args()
        if 'id' not in args:
            return "Bad Request", 400

        return expr_manager.stop_expr(args["id"])

    @token_required
    def put(self):
        args = request.get_json()
        if "id" not in args:
            return "invalid parameter", 400
        return expr_manager.heart_beat(args["id"])


class Anmt(Resource):
    def get(self):
        return db_adapter.find_first_object(Announcement, enabled=1).json()


class LoginResource(Resource):
    def post(self):
        body = request.get_json()
        provider = body["provider"]
        return login_providers[provider].login(body)

    @token_required
    def delete(self):
        return login_providers.values()[0].logout(g.user)

class TokenResource(Resource):
    def post(self):
        body = request.get_json()
        provider = body["provider"]
        return login_providers[provider].login(body)

# todo health page
class HealthResource(Resource):
    def get(self):
        return {
            "status": "OK"
        }


api.add_resource(DoCourse, "/api/course")
api.add_resource(StatusList, "/api/registerlist")
api.add_resource(Anmt, "/api/announcement")
api.add_resource(LoginResource, "/api/user/login")
api.add_resource(TokenResource, "/api/token/login")
api.add_resource(HealthResource, "/", "/health")

