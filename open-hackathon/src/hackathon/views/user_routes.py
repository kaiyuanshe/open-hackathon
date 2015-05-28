# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 
The MIT License (MIT)
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import sys

sys.path.append("..")

from hackathon import api
from flask_restful import Resource, reqparse
from hackathon.expr import expr_manager
from hackathon.user.login import login_providers, user_manager
from flask import g, request
from hackathon.decorators import token_required, hackathon_name_required
from hackathon.remote.guacamole import GuacamoleInfo
from hackathon.hack import hack_manager
from hackathon.registration.register_mgr import register_manager
from hackathon.hackathon_response import *
import json
from hackathon.enum import RGStatus


class GuacamoleResource(Resource):
    @token_required
    def get(self):
        return GuacamoleInfo().getConnectInfo()


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


class RegisterCheckEmailResource(Resource):
    # check email whether exist in the same hackathon registration
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('hid', type=int, location='args', required=True)
        parse.add_argument('email', type=str, location='args', required=True)
        args = parse.parse_args()
        return register_manager.is_email_registered(args['hid'], args['email'])


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

    @token_required
    @hackathon_name_required
    def put(self):
        args = request.get_json()
        args["status"] = RGStatus.UNAUDIT
        return register_manager.update_registration(args)


class UserHackathonListResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return hack_manager.get_user_hackathon_list(args['user_id'])


class UserExperimentResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=True)
        args = parser.parse_args()
        try:
            return expr_manager.get_expr_status(args['id'])
        except Exception as e:
            log.error(e)
            return internal_server_error("cannot find the experiment")

    @token_required
    def post(self):
        args = request.get_json()
        if "template_name" not in args or "hackathon" not in args:
            return "invalid parameter", 400
        template_name = args["template_name"]
        hackathon = args["hackathon"]
        try:
            return expr_manager.start_expr(hackathon, template_name, g.user.id)
        except Exception as err:
            log.error(err)
            return {"error": "fail to start due to '%s'" % err}, 500

    @token_required
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


class UserExperimentListResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return expr_manager.get_expr_list_by_user_id(args['user_id'])


def register_user_routes():
    """
    register API routes for hackathon UI user
    """

    # guacamole config api. "/api/guacamoleconfig" is depreciated, will be remoted soon
    api.add_resource(GuacamoleResource, "/api/guacamoleconfig", "/api/user/guacamoleconfig")

    # user api
    api.add_resource(UserResource, "/api/user/<int:id>")
    api.add_resource(UserLoginResource, "/api/user/login")

    # user-hackathon-relationship, or register, api
    api.add_resource(RegisterCheckEmailResource, "/api/user/registration/checkemail")
    api.add_resource(UserHackathonRelResource, "/api/user/registration")
    api.add_resource(UserHackathonListResource, "/api/user/registration/list")

    # experiment APIs
    api.add_resource(UserExperimentResource, "/api/user/experiment")
    api.add_resource(UserExperimentListResource, "/api/user/experiment/list")
