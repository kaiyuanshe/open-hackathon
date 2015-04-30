# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

from flask_restful import Resource, reqparse
from . import api, app
from expr import expr_manager
from expr.expr_mgr import open_check_expr, recycle_expr_scheduler
from database.models import Announcement, Hackathon, Template
from user.login import *
from flask import g, request
from database import db_adapter, db_session
from decorators import token_required, hackathon_name_required, admin_privilege_required
from user.user_functions import get_user_experiment
from health import report_health
from remote.guacamole import GuacamoleInfo
from hack import hack_manager
import time
from hackathon.registration.register_mgr import register_manager
from hackathon.template.template_mgr import template_manager
from hackathon_response import *


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


class UserResource(Resource):
    def get(self, id):
        return user_manager.get_user_by_id(id)


class UserLoginResource(Resource):
    def post(self):
        body = request.get_json()
        provider = body["provider"]
        return login_providers[provider].login(body)

    @token_required
    def delete(self):
        return login_providers.values()[0].logout(g.user)


class UserHackathonRelResource(Resource):
    @token_required
    @hackathon_name_required
    def get(self):
        return register_manager.get_registration_detail(g.user.id, g.hackathon)

    @token_required
    @hackathon_name_required
    def post(self):
        args = request.get_json()
        args["user_id"] = g.user.id
        return register_manager.create_registration(g.hackathon, args)


class AdminRegisterResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('rid', type=int, location='args', required=True)  # register_id
        args = parse.parse_args()
        rel = register_manager.get_registration_by_id(args["rid"])
        return rel.dic() if rel is None else not_found("not found")

    @admin_privilege_required
    def post(self):
        args = request.get_json()
        return register_manager.create_registration(g.hackathon, args)


    @admin_privilege_required
    def put(self):
        args = request.get_json()
        return register_manager.update_registration(args)

    @admin_privilege_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return register_manager.delete_registration(args)


class RegisterCheckEmailResource(Resource):
    # check email whether exist in the same hackathon registration
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('hid', type=int, location='args', required=True)
        parse.add_argument('email', type=str, location='args', required=True)
        args = parse.parse_args()
        return register_manager.is_email_registered(args['hid'], args['email'])


class AdminRegisterListResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('hackathon_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return register_manager.get_all_registration_by_hackathon_id(args['hackathon_id'])


class UserExperimentResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=True)
        args = parser.parse_args()
        try:
            cs = expr_manager.get_expr_status(args['id'])
        except Exception as e:
            log.error(e)
            return {"error": "Please Reload then Wait"}, 500
        if cs is not None:
            return cs
        else:
            return {"error": "Not Found"}, 404

    @token_required
    def post(self):
        args = request.get_json()
        if "cid" not in args or "hackathon" not in args:
            return "invalid parameter", 400
        cid = args["cid"]
        hackathon = args["hackathon"]
        try:
            return expr_manager.start_expr(hackathon, cid, g.user.id)
        except Exception as err:
            log.error(err)
            return {"error": "fail to start due to '%s'" % err}, 500

    # @token_required
    def delete(self):
        # id is experiment id
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=True)
        parser.add_argument('force', type=int, location='args', default=0)
        args = parser.parse_args()
        return expr_manager.stop_expr(args["id"], args['force'])

    @token_required
    def put(self):
        args = request.get_json()
        if args['id'] is None:
            return json.dumps({"error": "Bad request"}), 400
        return expr_manager.heart_beat(args["id"])


class BulletinResource(Resource):
    def get(self):
        announcement = db_adapter.find_first_object_by(Announcement, enabled=1)
        if announcement is not None:
            return announcement.dic()
        else:
            return Announcement(enabled=1, content="Welcome to Open Hackathon Platform!").dic()

    # todo bulletin post
    @admin_privilege_required
    def post(self):
        pass


class HealthResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, location='args')
        args = parser.parse_args()
        return report_health(args['q'])


class HackathonResource(Resource):
    @hackathon_name_required
    def get(self):
        return g.hackathon.dic()

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


class HackathonListResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args')
        parse.add_argument('status', type=int, location='args')
        args = parse.parse_args()

        return hack_manager.get_hackathon_list(args["user_id"], args["status"])


class HackathonStatResource(Resource):
    @hackathon_name_required
    def get(self):
        return hack_manager.get_hackathon_stat(g.hackathon)


class UserHackathonListResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return hack_manager.get_user_hackathon_list(args['user_id'])


class HackathonTemplateResource(Resource):
    # hid is hackathon id
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('hid', type=int, location='args', required=True)
        args = parse.parse_args()
        return map(lambda u: u.dic(), db_adapter.find_all_objects_by(Template, hackathon_id=args['hid']))


class UserExperimentListResource(Resource):
    @token_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('uid', type=int, location='args', required=True)
        args = parse.parse_args()
        return get_user_experiment(args['uid'])


class GuacamoleResource(Resource):
    @token_required
    def get(self):
        return GuacamoleInfo().getConnectInfo()


class CurrentTimeResource(Resource):
    def get(self):
        return {
            "currenttime": long(time.time() * 1000)
        }


class ExperimentPreAllocateResource(Resource):
    def get(self):
        open_check_expr()
        return ok("start default experiment")


class ExperimentRecycleResource(Resource):
    def get(self):
        recycle_expr_scheduler()
        return ok("Recycle inactive user experiment running on backgroud")


class TemplateResource(Resource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('hackathon_name', type=str, location='args', required=True)
        args = parse.parse_args()
        return template_manager.get_template_list(g.hackathon.name)


class AdminHackathonListResource(Resource):
    @admin_privilege_required
    def get(self):
        # todo move this logic to hack_manager
        hackathon_ids = hack_manager.get_hack_id_by_user_id(g.user.id)
        if -1 in hackathon_ids:
            hackathon_list = db_adapter.find_all_objects(Hackathon)
        else:
            hackathon_list = db_adapter.find_all_objects(Hackathon, Hackathon.id.in_(hackathon_ids))
        return map(lambda u: u.dic(), hackathon_list)


"""
health page
"""
api.add_resource(HealthResource, "/", "/health")

"""
announcement api
"""
api.add_resource(BulletinResource, "/api/bulletin")

"""
guacamole config api
"""
api.add_resource(GuacamoleResource, "/api/guacamoleconfig")

"""
user api
"""
api.add_resource(UserResource, "/api/user/<int:id>")
api.add_resource(UserLoginResource, "/api/user/login")

"""
user-hackathon-relationship, or register, api
"""
api.add_resource(RegisterCheckEmailResource, "/api/register/checkemail")
api.add_resource(AdminRegisterListResource, "/api/admin/register/list")
api.add_resource(AdminRegisterResource, "/api/admin/register")
api.add_resource(UserHackathonRelResource, "/api/user/hackathon")
api.add_resource(UserHackathonListResource, "/api/user/hackathon/list")

"""
hackathon api
"""
api.add_resource(HackathonResource, "/api/hackathon")
api.add_resource(HackathonListResource, "/api/hackathon/list")
api.add_resource(HackathonStatResource, "/api/hackathon/stat")
api.add_resource(AdminHackathonListResource, "/api/admin/hackathon/list")

"""
template api
"""
api.add_resource(HackathonTemplateResource, "/api/hackathon/template")
api.add_resource(TemplateResource, "/api/template/list")

"""
experiment api
"""
api.add_resource(UserExperimentResource, "/api/user/experiment")
api.add_resource(UserExperimentListResource, "/api/user/experiment/list")
api.add_resource(ExperimentPreAllocateResource, "/api/default/preallocate")
api.add_resource(ExperimentRecycleResource, "/api/default/recycle")

"""
system time api
"""
api.add_resource(CurrentTimeResource, "/api/currenttime")
