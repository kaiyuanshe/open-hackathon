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
from expr.expr_mgr import open_check_expr
from database.models import Announcement, Hackathon, Template
from user.login import *
from flask import g, request
from log import log
from database import db_adapter, db_session
from decorators import token_required, admin_token_required, hackathon_id_required
from user.user_functions import get_user_experiment, get_user_hackathon
from health import report_health
from remote.guacamole import GuacamoleInfo
from hack import hack_manager
import time
from admin.admin_mgr import admin_manager
from hackathon.registration.register_mgr import register_manager
from hackathon.template.template_mgr import template_manager


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


class RegisterListResource(Resource):
    # =======================================================return data start
    # [{"register_name":"zhang", "online":"1","submitted":"0"..."description":" "}]
    # =======================================================return data end
    @token_required
    def get(self):
        json_ret = map(lambda u: u.json(), user_manager.get_all_registration())
        return json_ret


class RegisterResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return register_manager.get_register_by_id(args)


    @token_required
    def post(self):
        args = request.get_json()
        hid = args['hackathon_id']
        if hid is None:
            return {}
        return register_manager.create_or_update_register(hid, args)


    @token_required
    def put(self):
        # update a Register
        pass


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
        return db_adapter.find_first_object_by(Announcement, enabled=1).json()

    # todo bulletin post
    @token_required
    def post(self):
        pass


class LoginResource(Resource):
    def post(self):
        body = request.get_json()
        provider = body["provider"]
        return login_providers[provider].login(body)

    @token_required
    def delete(self):
        return login_providers.values()[0].logout(g.user)


class HealthResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, location='args')
        args = parser.parse_args()
        return report_health(args['q'])


class HackathonResource(Resource):
    # hid is hackathon id
    @token_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('hid', type=int, location='args')
        parser.add_argument('name', type=str, location='args')
        args = parser.parse_args()
        if args['hid'] is None and args['name'] is None:
            return {}
        return hack_manager.get_hackathon_by_name_or_id(hack_id=args['hid'], name=args['name']).dic()

    # todo post
    @token_required
    def post(self):
        pass


class HackathonListResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('name', type=str, location='args')
        args = parse.parse_args()
        return hack_manager.get_hackathon_list(args["name"])


class HackathonStatResource(Resource):
    # hid is hackathon id
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('hid', type=int, location='args', required=True)
        args = parse.parse_args()
        return hack_manager.get_hackathon_stat(args['hid'])


class UserHackathonResource(Resource):
    # uid is user id
    @token_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('uid', type=int, location='args', required=True)
        args = parse.parse_args()
        return get_user_hackathon(args['uid'])

    # todo user hackathon post
    @token_required
    def post(self):
        pass

    # todo delete user hackathon
    @token_required
    def delete(self):
        pass


class HackathonTemplateResource(Resource):
    # hid is hackathon id
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('hid', type=int, location='args', required=True)
        args = parse.parse_args()
        return map(lambda u: u.json(), db_adapter.find_all_objects_by(Template, hackathon_id=args['hid']))


class UserExperimentListResource(Resource):
    # uid is user id
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


class UserResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('uid', type=int, location='args', required=True)
        args = parse.parse_args()
        return user_manager.get_user_by_id(args['uid'])


class CurrentTime(Resource):
    def get(self):
        return {
            "currenttime": long(time.time() * 1000)
        }


class DefaultExperiment(Resource):
    def get(self):
        open_check_expr()
        return {"Info": "start default experiment"}, 200


class TemplateResource(Resource):
    @token_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('hackathon_name', type=str, location='args', required=True)
        args = parse.parse_args()
        return template_manager.get_template_list(args['hackathon_name'])


api.add_resource(UserExperimentResource, "/api/user/experiment")
api.add_resource(RegisterListResource, "/api/register/list")
api.add_resource(RegisterResource, "/api/register")
api.add_resource(BulletinResource, "/api/bulletin")
api.add_resource(LoginResource, "/api/user/login")
api.add_resource(HackathonResource, "/api/hackathon")
api.add_resource(HackathonListResource, "/api/hackathon/list")
api.add_resource(HackathonTemplateResource, "/api/hackathon/template")
api.add_resource(HackathonStatResource, "/api/hackathon/stat")
api.add_resource(HealthResource, "/", "/health")
api.add_resource(UserHackathonResource, "/api/user/hackathon")
api.add_resource(UserExperimentListResource, "/api/user/experiment/list")
api.add_resource(GuacamoleResource, "/api/guacamoleconfig")
api.add_resource(UserResource, "/api/user")
api.add_resource(CurrentTime, "/api/currenttime")
api.add_resource(DefaultExperiment, "/api/default/experiment")
api.add_resource(TemplateResource, "/api/template/list")

# ------------------------------ APIs for admin-site --------------------------------


class AdminHackathonListResource(Resource):
    @admin_token_required
    def get(self):
        hackathon_ids = admin_manager.get_hack_id_by_admin_id(g.admin.id)
        if -1 in hackathon_ids:
            hackathon_list = db_adapter.find_all_objects(Hackathon)
        else:
            hackathon_list = db_adapter.find_all_objects(Hackathon, Hackathon.id.in_(hackathon_ids))
        return map(lambda u: u.dic(), hackathon_list)


class AdminRegisterListResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('hackathon_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return register_manager.get_register_list(args['hackathon_id'])


class AdminRegisterResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return register_manager.get_register_by_id(args)


    @admin_token_required
    @hackathon_id_required
    def post(self):
        args = request.get_json()
        return register_manager.create_or_update_register(g.hackathon_id, args)


    @admin_token_required
    @hackathon_id_required
    def put(self):
        # update a Register
        args = request.get_json()
        return register_manager.create_or_update_register(g.hackathon_id, args)


    @admin_token_required
    @hackathon_id_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return register_manager.delete_register(args)


api.add_resource(AdminHackathonListResource, "/api/admin/hackathons")
api.add_resource(AdminRegisterListResource, "/api/admin/register/list")
api.add_resource(AdminRegisterResource, "/api/admin/register")
