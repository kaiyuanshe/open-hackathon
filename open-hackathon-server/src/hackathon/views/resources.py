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
from hackathon.hackathon_response import bad_request, not_found, ok
from hackathon_resource import HackathonResource
from hackathon.constants import RGStatus

hackathon_manager = RequiredFeature("hackathon_manager")
user_manager = RequiredFeature("user_manager")
user_profile_manager = RequiredFeature("user_profile_manager")
register_manager = RequiredFeature("register_manager")
hackathon_template_manager = RequiredFeature("hackathon_template_manager")
template_library = RequiredFeature("template_library")
team_manager = RequiredFeature("team_manager")
azure_cert_manager = RequiredFeature("azure_cert_manager")
expr_manager = RequiredFeature("expr_manager")
admin_manager = RequiredFeature("admin_manager")
guacamole = RequiredFeature("guacamole")
docker_host_manager = RequiredFeature("docker_host_manager")

util = RequiredFeature("util")
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
        context = self.context()
        return template_library.get_template_info_by_id(context.id)

    # create template
    @token_required
    def post(self):
        args = request.get_json()
        return template_library.create_template(args)

    # modify template
    @token_required
    def put(self):
        args = request.get_json()
        return template_library.update_template(args)

    # delete template
    @token_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return template_library.delete_template(args['id'])


class TemplateCreateByFileResource(HackathonResource):
    # create template by file
    @token_required
    def post(self):
        return template_library.create_template_by_file()


class TemplateListResource(HackathonResource):
    def get(self):
        return template_library.search_template(request.args)


"""Resources for hackathon query that not related to specific user or admin"""


class HackathonResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return hackathon_manager.get_hackathon_detail(g.hackathon)


class HackathonListResource(HackathonResource):
    def get(self):
        return hackathon_manager.get_hackathon_list(request.args)


class HackathonStatResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return hackathon_manager.get_hackathon_stat(g.hackathon)


class HackathonRegistrationListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('num', type=int, location='args', default=5)
        args = parse.parse_args()
        return register_manager.get_hackathon_registration_list(args['num'])


"""Resources for user(participant) to join hackathon"""


class GuacamoleResource(HackathonResource):
    @token_required
    def get(self):
        return guacamole.getConnectInfo()


class UserLoginResource(HackathonResource):
    '''User login/logout processing'''

    def get(self):
        '''Get user by id'''
        return user_manager.load_user(self.context().id)

    def post(self):
        '''user login'''
        context = self.context()
        return user_manager.login(context.provider, context)

    @token_required
    def delete(self):
        '''User logout'''
        return user_manager.logout(g.user.id)


class CurrentUserResource(HackathonResource):
    @token_required
    def get(self):
        return user_manager.user_display_info(g.user)


class UserListResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return user_manager.get_user_fezzy_search(g.hackathon, self.context())


class UserProfileResource(HackathonResource):
    @token_required
    def get(self):
        user_id = g.user.id
        info = user_profile_manager.get_user_profile(user_id)
        if info is not None:
            return info.dic()
        else:
            return not_found("User doesn't have profile info yet.")

    @token_required
    def post(self):
        args = request.get_json()
        args["user_id"] = g.user.id
        return user_profile_manager.create_user_profile(args)

    @token_required
    def put(self):
        args = request.get_json()
        args["user_id"] = g.user.id
        return user_profile_manager.update_user_profile(args)


class UserTemplateListResource(HackathonResource):
    @token_required
    @hackathon_name_required
    def get(self):
        return hackathon_template_manager.get_user_templates(g.user, g.hackathon)


class UserRegistrationResource(HackathonResource):
    @token_required
    @hackathon_name_required
    def get(self):
        return register_manager.get_registration_detail(g.user, g.hackathon)

    @token_required
    @hackathon_name_required
    def post(self):
        args = {
            "user_id": g.user.id,
            "hackathon_id": g.hackathon.id
        }
        return register_manager.create_registration(g.hackathon, g.user, args)


class UserHackathonListResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return hackathon_manager.get_user_hackathon_list_with_detail(args['user_id'])


class UserHackathonLikeResource(HackathonResource):
    @hackathon_name_required
    @token_required
    def post(self):
        return hackathon_manager.like_hackathon(g.user, g.hackathon)

    @hackathon_name_required
    @token_required
    def delete(self):
        return hackathon_manager.unlike_hackathon(g.user, g.hackathon)


class UserExperimentResource(HackathonResource, Component):
    def get(self):
        return expr_manager.get_expr_status(int(self.context().id))

    @token_required
    def post(self):
        context = self.context()
        return expr_manager.start_expr(g.user.id, context.template_name, context.get("hackathon_name"))

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
        return expr_manager.heart_beat(int(self.context().id))


class TeamResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=str, location='args', required=True)
        args = parse.parse_args()
        return team_manager.get_team_by_id(args["id"])

    # @token_required
    # @hackathon_name_required
    # def post(self):
    #     args = request.get_json()
    #     return team_manager.create_team(args)

    @token_required
    @hackathon_name_required
    def put(self):
        args = request.get_json()
        return team_manager.update_team(args)

    @token_required
    def delete(self):
        return team_manager.dismiss_team(g.user, self.context().id)


class TeamScoreResource(HackathonResource):
    @token_required
    def get(self):
        return team_manager.get_score(g.user, self.context().team_id)

    @token_required
    def post(self):
        return team_manager.score_team(g.user, self.context())

    @token_required
    def put(self):
        return team_manager.score_team(g.user, self.context())


class TeamShowResource(HackathonResource):
    def get(self):
        return team_manager.get_team_show_list(self.context().team_id)

    @token_required
    def post(self):
        return team_manager.add_team_show(g.user, self.context())

    @token_required
    def delete(self):
        return team_manager.delete_team_show(g.user, self.context().id)


class HackathonTeamShowResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        show_type = request.args.get("type")
        limit = request.args.get("limit", 6)
        return team_manager.get_hackathon_show_list(g.hackathon.id, show_type, limit)


class TeamMemberResource(HackathonResource):
    @token_required
    def post(self):
        return team_manager.join_team(g.user, self.context().team_id)

    @token_required
    def put(self):
        ctx = self.context()
        return team_manager.update_team_member_status(g.user, ctx.id, ctx.status)

    @token_required
    def delete(self):
        ctx = self.context()
        return team_manager.kick_or_leave(g.user, ctx.team_id, ctx.user_id)


class HackathonTeamListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('name', type=str, location='args', required=False)
        parse.add_argument('number', type=int, location='args', required=False)
        result = parse.parse_args()
        return team_manager.get_hackathon_team_list(g.hackathon.id, result['name'], result['number'])


class TeamMemberListResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('team_id', type=int, location='args', required=True)
        args = parse.parse_args()

        return team_manager.get_team_members(args["team_id"])


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


class TalentResource(HackathonResource):
    def get(self):
        return user_manager.get_talents()


"""Resources for hackathon admin to manage hackathon and hackathon related resources and features"""


class AdminHackathonResource(HackathonResource):
    """Resource for admin to create/update hackathon

    url path: /api/admin/hackathon
    """

    @hackathon_name_required
    def get(self):
        return hackathon_manager.get_hackathon_detail(g.hackathon)

    @token_required
    def post(self):
        return hackathon_manager.create_new_hackathon(self.context())

    @admin_privilege_required
    def put(self):
        return hackathon_manager.update_hackathon(request.get_json())


class AdminHackathonConfigResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return hackathon_manager.get_all_properties(g.hackathon)

    @admin_privilege_required
    def post(self):
        return hackathon_manager.set_basic_property(g.hackathon, self.context())

    @admin_privilege_required
    def put(self):
        return hackathon_manager.set_basic_property(g.hackathon, self.context())

    @admin_privilege_required
    def delete(self):
        return hackathon_manager.set_basic_property(g.hackathon, self.context().key)


class AdminHackathonOrganizerResource(HackathonResource):
    def get(self):
        return hackathon_manager.qet_organizer_by_id(self.context().id)

    @admin_privilege_required
    def post(self):
        return hackathon_manager.create_hackathon_organizer(g.hackathon, request.get_json())

    @admin_privilege_required
    def put(self):
        return hackathon_manager.update_hackathon_organizer(g.hackathon, request.get_json())

    @admin_privilege_required
    def delete(self):
        return hackathon_manager.delete_hackathon_organizer(g.hackathon, self.context().id)


class AdminHackathonTags(HackathonResource):
    @hackathon_name_required
    def get(self):
        return hackathon_manager.get_hackathon_tags(g.hackathon)

    @admin_privilege_required
    def post(self):
        tags = request.get_data().split(",")
        return hackathon_manager.set_hackathon_tags(g.hackathon, tags)

    @admin_privilege_required
    def put(self):
        tags = request.get_data().split(",")
        return hackathon_manager.set_hackathon_tags(g.hackathon, tags)


class HackathonTagNamesResource(HackathonResource):
    def get(self):
        return hackathon_manager.get_distinct_tags()


class HackathonCheckNameResource(HackathonResource):
    def get(self):
        context = self.context()
        return hackathon_manager.is_hackathon_name_existed(context.name)


class AdminHackathonListResource(HackathonResource):
    @token_required
    def get(self):
        return hackathon_manager.get_entitled_hackathon_list_with_detail(g.user)


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
        return register_manager.update_registration(self.context())

    @admin_privilege_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return register_manager.delete_registration(args)


class AdminHackathonTemplateListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return hackathon_template_manager.get_templates_with_detail_by_hackathon(g.hackathon.id)


class AdminHackathonTemplateResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        args = request.get_json()
        if "template_id" not in args:
            return bad_request("template id invalid")
        return hackathon_template_manager.add_template_to_hackathon(args['template_id'])

    @admin_privilege_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('template_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return hackathon_template_manager.delete_template_from_hackathon(args['template_id'])


class AdminExperimentResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        args = request.get_json()
        if 'name' not in args:
            return bad_request('template name name invalid')
        template_name = args['name']
        return expr_manager.start_expr(g.user.id, template_name, g.hackathon.name)

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
    """Resource to add/delete administrators/judges of a hackathon"""

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


class AdminTeamScoreListResource(HackathonResource):
    @token_required
    def get(self):
        return team_manager.get_score(g.user, self.context().team_id)


class HackathonAwardResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        return hackathon_manager.create_hackathon_award(g.hackathon, self.context())

    @admin_privilege_required
    def put(self):
        return hackathon_manager.update_hackathon_award(g.hackathon, self.context())

    @admin_privilege_required
    def delete(self):
        return hackathon_manager.delete_hackathon_award(g.hackathon, self.context().id)


class HackathonAwardListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return hackathon_manager.list_hackathon_awards(g.hackathon)


class TeamAwardResource(HackathonResource):
    def get(self):
        return team_manager.query_team_awards(self.context().team_id)

    @admin_privilege_required
    def post(self):
        return team_manager.grant_award_to_team(g.hackathon, self.context())

    @admin_privilege_required
    def delete(self):
        return team_manager.cancel_team_award(g.hackathon, self.context().id)


class HackathonGrantedAwardsResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return team_manager.get_granted_awards(g.hackathon)


class GranteAwardsResource(HackathonResource):
    def get(self):
        return team_manager.get_all_granted_awards(self.context().limit)


class AdminHostserverListResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return docker_host_manager.get_docker_hosts_list(g.hackathon.id)


class AdminHostserverResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return docker_host_manager.get_and_check_host_server(self.context().id)

    @admin_privilege_required
    def post(self):
        return docker_host_manager.create_host_server(g.hackathon.id, self.context())

    @admin_privilege_required
    def put(self):
        return docker_host_manager.update_host_server(self.context())

    @admin_privilege_required
    def delete(self):
        return docker_host_manager.delete_host_server(self.context().id)


class AdminHackathonCanOnLineResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return hackathon_manager.check_hackathon_online(g.hackathon)


class AdminHackathonNoticeResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return hackathon_manager.get_hackathon_notice(self.context().id)

    @admin_privilege_required
    def post(self):
        ctx = self.context()
        return hackathon_manager.create_hackathon_notice(g.hackathon.id, int(ctx.get('event', 0)), int(ctx.get('category', 0)), ctx)

    @admin_privilege_required
    def put(self):
        return hackathon_manager.update_hackathon_notice(self.context())

    @admin_privilege_required
    def delete(self):
        return hackathon_manager.delete_hackathon_notice(self.context().id)


class HackathonNoticeListResource(HackathonResource):
    def get(self):
        return hackathon_manager.get_hackathon_notice_list(self.context())
