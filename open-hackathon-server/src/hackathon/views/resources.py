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
import time
import json

from flask import g, request
from flask_restful import reqparse

from hackathon import RequiredFeature, Component
from hackathon.decorators import hackathon_name_required, token_required, admin_privilege_required
from hackathon.health import report_health
from hackathon.hackathon_response import bad_request, not_found, internal_server_error
from hackathon_resource import HackathonResource
from hackathon.constants import RGStatus

hackathon_manager = RequiredFeature("hackathon_manager")
user_manager = RequiredFeature("user_manager")
register_manager = RequiredFeature("register_manager")
template_manager = RequiredFeature("template_manager")
team_manager = RequiredFeature("team_manager")
azure_cert_manager = RequiredFeature("azure_cert_manager")
expr_manager = RequiredFeature("expr_manager")
admin_manager = RequiredFeature("admin_manager")
guacamole = RequiredFeature("guacamole")

"""Resources for OHP itself"""


class HealthResource(HackathonResource):
    def get(self):
        context = self.context()
        return report_health(context.get("q"))


class CurrentTimeResource(HackathonResource):
    def get(self):
        return {
            "currenttime": long(time.time() * 1000)
        }


"""Resources for templates library"""


class TemplateResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=False)
        args = parse.parse_args()
        template = template_manager.get_template_by_id(args['id'])
        return template.dic() if template is not None else not_found("not found")

    # create template
    @token_required
    def post(self):
        args = request.get_json()
        return template_manager.create_template(args)

    # modify template
    @token_required
    def put(self):
        args = request.get_json()
        return template_manager.update_template(args)

    # delete template
    @token_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return template_manager.delete_template(args['id'])


class TemplateCreateByFileResource(HackathonResource):
    # create template by file
    @token_required
    def post(self):
        return template_manager.create_template_by_file()


class TemplateListResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('status', type=int, location='args', required=False)
        parse.add_argument('name', type=str, location='args', required=False)
        parse.add_argument('description', type=str, location='args', required=False)
        args = parse.parse_args()
        templates = template_manager.get_template_list(status=args['status'],
                                                       name=args['name'],
                                                       description=args['description'])
        return map(lambda x: x.dic(), templates)


"""Resources for hackathon query that not related to specific user or admin"""


class HackathonResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return g.hackathon.dic()


class HackathonListResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args')
        parse.add_argument('status', type=int, location='args')
        args = parse.parse_args()
        return hackathon_manager.get_hackathon_list(args["user_id"], args["status"])


class HackathonStatResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return hackathon_manager.get_hackathon_stat(g.hackathon)


class HackathonTeamListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('name', type=str, location='args', required=False)
        parse.add_argument('number', type=int, location='args', required=False)
        result = parse.parse_args()
        return team_manager.get_hackathon_team_list(g.hackathon.id, result['name'], result['number'])


class HackathonRegistrationListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('num', type=int, location='args', default=5)
        args = parse.parse_args()
        return register_manager.get_hackathon_registration(args['num'])


"""Resources for user(participant) to join hackathon"""


class GuacamoleResource(HackathonResource):
    @token_required
    def get(self):
        return guacamole.getConnectInfo()


class CurrentUserResource(HackathonResource):
    @token_required
    def get(self):
        return user_manager.user_display_info(g.user)


class UserProfileResource(HackathonResource):
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


class UserTemplateListResource(HackathonResource):
    @token_required
    @hackathon_name_required
    def get(self):
        return template_manager.get_user_templates(g.user, g.hackathon)


class UserRegistrationResource(HackathonResource):
    @token_required
    @hackathon_name_required
    def get(self):
        return register_manager.get_registration_detail(g.user, g.hackathon)

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


class UserHackathonListResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return hackathon_manager.get_user_hackathon_list(args['user_id'])


class UserExperimentResource(HackathonResource, Component):
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


class UserExperimentListResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return expr_manager.get_expr_list_by_user_id(args['user_id'])


class TeamResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('team_name', type=str, location='args')
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


class UserTeamsResource(HackathonResource):
    @token_required
    def get(self):
        return team_manager.get_teams_by_user(g.user.id)


class TeamListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return team_manager.get_team_by_hackathon(g.hackathon.id)


class TeamMemberResource(HackathonResource):
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


class TeamMemberListResource(HackathonResource):
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


class TeamLeaderResource(HackathonResource):
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


class TeamTemplateResource(HackathonResource):
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


"""Resources for hackathon admin to manage hackathon and hackathon related resources and features"""


class AdminHackathonResource(HackathonResource):
    """Resource for admin to create/update hackathon

    url path: /api/admin/hackathon
    """

    @hackathon_name_required
    def get(self):
        return g.hackathon.dic()

    @token_required
    def post(self):
        return hackathon_manager.create_new_hackathon(self.context())

    @admin_privilege_required
    def put(self):
        return hackathon_manager.update_hackathon(request.get_json())


class HackathonCheckNameResource(HackathonResource):
    def get(self):
        context = self.context()
        return hackathon_manager.is_hackathon_name_existed(context.name)


class AdminHackathonListResource(HackathonResource):
    @token_required
    def get(self):
        return hackathon_manager.get_entitled_hackathon_list(g.user.id)


class AdminAzureResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return azure_cert_manager.get_certificates(g.hackathon)

    @admin_privilege_required
    def post(self):
        ctx = self.context()
        return azure_cert_manager.create_certificate(ctx.subscription_id, ctx.management_host, g.hackathon)

    @admin_privilege_required
    def delete(self):
        ctx = self.context()
        return azure_cert_manager.delete_certificate(ctx.certificate_id, g.hackathon)


class AdminRegisterListResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return register_manager.get_hackathon_registration_list()


class AdminRegisterResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)  # register_id
        args = parse.parse_args()
        rel = register_manager.get_registration_by_id(args["id"])
        return rel.dic() if rel is not None else not_found("not found")

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


class AdminHackathonTemplateListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        templates = template_manager.get_templates_by_hackathon_id(g.hackathon.id)
        return map(lambda x: x.dic(), templates)


class AdminHackathonTemplateResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        args = request.get_json()
        if "template_id" not in args:
            return bad_request("template id invalid")
        return template_manager.add_template_to_hackathon(args['template_id'])

    @admin_privilege_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('template_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return template_manager.delete_template_from_hackathon(args['template_id'])


class AdminExperimentResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        args = request.get_json()
        if 'name' not in args:
            return bad_request('template name name invalid')
        template_name = args['name']
        user_id = g.user.id
        hackathon_name = g.hackathon.name
        return expr_manager.start_expr(hackathon_name, template_name, user_id)

    @admin_privilege_required
    def delete(self):
        args = request.get_json()
        if 'experiment_id' not in args:
            return bad_request('experiment id invalid')
        return expr_manager.stop_expr(args['experiment_id'])


class AdminExperimentListResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_name', type=str, location='args')
        parse.add_argument('status', type=int, location='args')
        args = parse.parse_args()
        return expr_manager.get_expr_list_by_hackathon_id(g.hackathon.id,
                                                          user_name=args['user_name'],
                                                          status=args['status'])


class AdminHackathonFileResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        return hackathon_manager.upload_files()

    def delete(self):
        # TODO call storage api to delete file
        return True


class HackathonAdminListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return admin_manager.get_admins_by_hackathon(g.hackathon)


class HackathonAdminResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        args = request.get_json()
        return admin_manager.add_admin(args)

    @admin_privilege_required
    def put(self):
        args = request.get_json()
        return admin_manager.update_admin(args)

    @admin_privilege_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return admin_manager.delete_admin(args['id'])
