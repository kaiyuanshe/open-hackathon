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

from hackathon import api, RequiredFeature, Component
from flask import g, request
from flask_restful import Resource, reqparse
from hackathon.decorators import token_required, hackathon_name_required
from hackathon.hackathon_response import internal_server_error, not_found, bad_request
import json
from hackathon.constants import RGStatus

hackathon_manager = RequiredFeature("hackathon_manager")
register_manager = RequiredFeature("register_manager")
expr_manager = RequiredFeature("expr_manager")
user_manager = RequiredFeature("user_manager")
guacamole = RequiredFeature("guacamole")
team_manager = RequiredFeature("team_manager")


class GuacamoleResource(Resource):
    @token_required
    def get(self):
        return guacamole.getConnectInfo()


class CurrentUserResource(Resource):
    @token_required
    def get(self):
        return user_manager.user_display_info(g.user)


class UserHackathonRelResource(Resource, Component):
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
        return hackathon_manager.get_user_hackathon_list(args['user_id'])


class UserExperimentResource(Resource, Component):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, location='args', required=True)
        args = parser.parse_args()
        try:
            return expr_manager.get_expr_status(args['id'])
        except Exception as e:
            self.log.error(e)
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
            self.log.error(err)
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


class TeamMemberListResource(Resource):
    @token_required
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('team_name', type=str, location='args')
        args = parse.parse_args()

        if args["team_name"]:
            return team_manager.get_team_members_by_name(g.hackathon.id, args["team_name"])
        else:
            return team_manager.get_team_members_by_user(g.hackathon.id, g.user.id)


class UserProfileResource(Resource):
    @token_required
    def get(self):
        user_id = g.user.id
        info = register_manager.get_user_profile(user_id)
        if info is not None:
            return info.dic()
        else:
            return not_found("User doesn't have profile info yet.")

    @token_required
    def post(self):
        args = request.get_json()
        args["user_id"] = g.user.id
        return register_manager.create_user_profile(args)

    @token_required
    def put(self):
        args = request.get_json()
        args["user_id"] = g.user.id
        return register_manager.update_user_profile(args)


class TeamTemplateResource(Resource):
    @token_required
    @hackathon_name_required
    def post(self):
        args = request.get_json()
        return team_manager.add_template_for_team(args)

    @token_required
    @hackathon_name_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('template_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return team_manager.delete_template_from(args['template_id'])


class TeamResource(Resource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('team_name', type=str, location='args', required=True)
        args = parse.parse_args()
        return team_manager.get_team_by_name(g.hackathon.id, args["team_name"])

    @token_required
    @hackathon_name_required
    def post(self):
        args = request.get_json()
        return team_manager.create_team(args)

    @token_required
    @hackathon_name_required
    def put(self):
        args = request.get_json()
        return team_manager.update_team(args)

    @token_required
    @hackathon_name_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('team_name', type=str, location='args', required=True)
        args = parse.parse_args()
        return team_manager.dismiss_team(g.hackathon.id, args["team_name"])


class TeamMemberResource(Resource):
    @token_required
    @hackathon_name_required
    def post(self):
        args = request.get_json()
        if "team_name" not in args:
            return bad_request("Team name is required")
        return team_manager.join_team(g.hackathon.id, args["team_name"], g.user)

    @token_required
    @hackathon_name_required
    def put(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='json', required=True)
        parse.add_argument("status", type=int, location="json", required=True)
        parse.add_argument("team_name", type=str, location="json", required=True)
        args = parse.parse_args()
        return team_manager.update_team_member_status(g.hackathon.id,
                                                      args["team_name"],
                                                      args["member"],
                                                      g.user,
                                                      args["user_id"])

    @token_required
    @hackathon_name_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args', required=True)
        parse.add_argument('team_name', type=str, location='args', required=True)
        args = parse.parse_args()
        if g.user.id == args["user_id"]:
            return team_manager.leave_team(g.hackathon.id, args["team_name"])
        else:
            return team_manager.kick(args["team_name"], args["user_id"])


class TeamLeaderResource(Resource):
    @token_required
    @hackathon_name_required
    def put(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='json', required=True)
        parse.add_argument('team_name', type=str, location='json', required=True)
        args = parse.parse_args()
        return team_manager.promote_leader(g.hackathon.id,
                                           args["team_name"],
                                           args["user_id"])


def register_user_routes():
    """
    register API routes for hackathon UI user
    """

    # guacamole config API. "/api/guacamoleconfig" is depreciated, will be removed soon
    api.add_resource(GuacamoleResource, "/api/guacamoleconfig", "/api/user/guacamoleconfig")

    # user API
    api.add_resource(CurrentUserResource, "/api/user")

    # user-hackathon-relationship, or register, API
    api.add_resource(UserHackathonRelResource, "/api/user/registration")
    api.add_resource(UserHackathonListResource, "/api/user/registration/list")

    # experiment API
    api.add_resource(UserExperimentResource, "/api/user/experiment")
    api.add_resource(UserExperimentListResource, "/api/user/experiment/list")

    # team API
    api.add_resource(TeamResource, "/api/team")
    api.add_resource(TeamMemberResource, "/api/team/member")
    api.add_resource(TeamMemberListResource, "/api/team/member/list")
    api.add_resource(TeamLeaderResource, "/api/team/leader")

    # user profile API
    api.add_resource(UserProfileResource, "/api/user/profile")

    # team template API
    api.add_resource(TeamTemplateResource, "/api/team/template")
