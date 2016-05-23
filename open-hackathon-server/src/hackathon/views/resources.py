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

from flask import g, request
from flask_restful import reqparse

from hackathon import RequiredFeature, Component
from hackathon.decorators import hackathon_name_required, token_required, admin_privilege_required
from hackathon.health import report_health
from hackathon.hackathon_response import bad_request, not_found
from hackathon_resource import HackathonResource

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
        template = template_library.get_template_info_by_id(context.id)
        if template:
            return template.dic()
        return not_found("template cannot be found by id %s" % context.id)

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
        parse.add_argument('id', type=str, location='args', required=True)
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
        return register_manager.get_hackathon_registration_list(g.hackathon.id, args['num'])


"""Resources for user(participant) to join hackathon"""


class GuacamoleResource(HackathonResource):
    @token_required
    def get(self):
        return guacamole.getConnectInfo()


class UserLoginResource(HackathonResource):
    """User login/logout processing"""

    def get(self):
        """Get user by id"""
        return user_manager.load_user(self.context().id)

    def post(self):
        """user login"""
        context = self.context()
        return user_manager.login(context.provider, context)

    @token_required
    def delete(self):
        """User logout"""
        return user_manager.logout(g.user.id)


class UserResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument("user_id", type=str, location="args", required=False)
        args = parse.parse_args()

        uid = args["user_id"] or None

        if uid:
            user = user_manager.get_user_by_id(uid)
        elif user_manager.validate_login():
            user = user_manager.get_user_by_id(g.user.id)
        else:
            return bad_request("must login or provide a user id")

        return user_manager.cleaned_user_dic(user)


class UserListResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return user_manager.get_user_fezzy_search(g.hackathon, self.context())


class UserProfileResource(HackathonResource):
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


class UserPictureResource(HackathonResource):
    @token_required
    def put(self):
        args = request.get_json()
        return user_manager.update_user_avatar_url(g.user, args["url"])


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
            "hackathon_id": g.hackathon.id}

        return register_manager.create_registration(g.hackathon, g.user, args)


class UserHackathonListResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=str, location='args', required=False)
        args = parse.parse_args()
        user_id = args["user_id"] or g.user.id
        return hackathon_manager.get_user_hackathon_list_with_detail(user_id)


class UserHackathonLikeResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=str, location='args', required=False)
        args = parse.parse_args()
        user_id = args["user_id"] or g.user.id
        return hackathon_manager.get_userlike_all_hackathon(user_id)

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
        return expr_manager.get_expr_status_and_confirm_starting(self.context().id)

    @token_required
    def post(self):
        context = self.context()
        return expr_manager.start_expr(g.user, context.template_name, context.get("hackathon_name"))

    @token_required
    def delete(self):
        # id is experiment id
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str, location='args', required=True)
        args = parser.parse_args()
        return expr_manager.stop_expr(args["id"])

    @token_required
    def put(self):
        return expr_manager.heart_beat(self.context().id)


class MyTeamResource(HackathonResource):
    @token_required
    @hackathon_name_required
    def get(self):
        return team_manager.get_my_current_team(g.hackathon, g.user)


class UserTeamShowResource(HackathonResource):
    def get(self):
        user_id = self.context().user_id if "user_id" in self.context() else None
        if user_id:
            return team_manager.get_team_show_list_by_user(user_id)
        elif user_manager.validate_login():
            return team_manager.get_team_show_list_by_user(g.user.id)
        else:
            return bad_request("must login or provide a user id")


class UserNoticeReadResource(HackathonResource):
    @token_required
    def put(self):
        return hackathon_manager.check_notice_and_set_read_if_necessary(self.context().id)


class UserFileResource(HackathonResource):
    @token_required
    def post(self):
        return user_manager.upload_files(g.user.id, self.context().file_type)

    @token_required
    def delete(self):
        # TODO call storage api to delete file
        return True


class TeamResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return team_manager.get_team_by_id(self.context().id)

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
        parse = reqparse.RequestParser()
        parse.add_argument("limit", type=int, location='args')
        parse.add_argument("type", type=str, location='args')
        args = parse.parse_args()

        show_type = args.get("type")
        limit = args.get("limit", 6)

        return team_manager.get_hackathon_show_list(g.hackathon.id, show_type, limit)


class TeamMemberResource(HackathonResource):
    @token_required
    def post(self):
        return team_manager.join_team(g.user, self.context().team_id)

    @token_required
    def put(self):
        ctx = self.context()
        return team_manager.update_team_member_status(g.user, ctx.team_id, ctx.user_id, ctx.status)

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
        parse.add_argument('team_id', type=str, location='args', required=True)
        args = parse.parse_args()

        ret = team_manager.get_team_members(args["team_id"])
        if not ret:
            return not_found()
        return ret


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
        parse.add_argument('template_id', type=str, location='args', required=True)
        args = parse.parse_args()
        return team_manager.delete_template_from_team(args['template_id'])


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

    @admin_privilege_required
    def delete(self):
        return hackathon_manager.delete_hackathon()


class AdminHackathonConfigResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return hackathon_manager.get_all_properties(g.hackathon)

    @admin_privilege_required
    def post(self):
        return hackathon_manager.set_basic_property(g.hackathon, self.context().to_dict())

    @admin_privilege_required
    def put(self):
        return hackathon_manager.set_basic_property(g.hackathon, self.context().to_dict())

    @admin_privilege_required
    def delete(self):
        return hackathon_manager.delete_basic_property(g.hackathon, self.context().to_dict().values())


class AdminHackathonOrganizerResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        return hackathon_manager.create_hackathon_organizer(g.hackathon, self.context())

    @admin_privilege_required
    def put(self):
        return hackathon_manager.update_hackathon_organizer(g.hackathon, self.context())

    @admin_privilege_required
    def delete(self):
        return hackathon_manager.delete_hackathon_organizer(g.hackathon, self.context().id)


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
        return admin_manager.get_entitled_hackathons_list(g.user)


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


class AdminAzureCheckSubIdResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        ctx = self.context()
        return azure_cert_manager.check_sub_id(ctx.subscription_id)


class AdminRegisterListResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return register_manager.get_hackathon_registration_list(g.hackathon.id)


class AdminRegisterResource(HackathonResource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument("id", type=str, location="args", required=True)  # register_id

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
        parse.add_argument('id', type=str, location='args', required=True)
        args = parse.parse_args()
        return register_manager.delete_registration(args)


class AdminHackathonTemplateListResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return hackathon_template_manager.get_templates_with_detail_by_hackathon(g.hackathon)


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
        parse.add_argument('template_id', type=str, location='args', required=True)
        args = parse.parse_args()
        return hackathon_template_manager.delete_template_from_hackathon(args['template_id'])


class AdminExperimentResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        args = request.get_json()
        if 'name' not in args:
            return bad_request('template name name invalid')
        template_name = args['name']
        return expr_manager.start_expr(g.user, template_name, g.hackathon.name)

    @admin_privilege_required
    def put(self):
        return expr_manager.restart_stopped_expr(self.context().experiment_id)

    @admin_privilege_required
    def delete(self):
        args = request.get_json()
        if 'experiment_id' not in args:
            return bad_request('experiment id invalid')
        return expr_manager.stop_expr(args['experiment_id'])


class AdminExperimentListResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return expr_manager.get_expr_list_by_hackathon_id(g.hackathon, self.context())


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
        parse.add_argument('id', type=str, location='args', required=True)
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
        return team_manager.cancel_team_award(g.hackathon, self.context().team_id, self.context().award_id)


class HackathonGrantedAwardsResource(HackathonResource):
    @hackathon_name_required
    def get(self):
        return team_manager.get_granted_awards(g.hackathon)


class GranteAwardsResource(HackathonResource):
    def get(self):
        return team_manager.get_all_granted_awards(self.context().get("limit", 10))


class AdminHostserverListResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return docker_host_manager.get_docker_hosts_list(g.hackathon)


class AdminHostserverResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return docker_host_manager.get_and_check_host_server(self.context().id)

    @admin_privilege_required
    def post(self):
        return docker_host_manager.add_host_server(g.hackathon, self.context())

    @admin_privilege_required
    def put(self):
        return docker_host_manager.update_host_server(self.context())

    @admin_privilege_required
    def delete(self):
        return docker_host_manager.delete_host_server(self.context().id)


class AdminHackathonOnLineResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        return hackathon_manager.hackathon_online(g.hackathon)


class AdminHackathonApplyOnLineResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        return hackathon_manager.apply_online_hackathon(g.hackathon)


class AdminHackathonOffLineResource(HackathonResource):
    @admin_privilege_required
    def post(self):
        return hackathon_manager.hackathon_offline(g.hackathon)


class AdminHackathonNoticeResource(HackathonResource):
    @admin_privilege_required
    def get(self):
        return hackathon_manager.get_hackathon_notice(self.context().id)

    @admin_privilege_required
    def post(self):
        ctx = self.context()
        return hackathon_manager.create_hackathon_notice(g.hackathon.id, int(ctx.get('event', 0)),
                                                         int(ctx.get('category', 0)), ctx)

    @admin_privilege_required
    def put(self):
        return hackathon_manager.update_hackathon_notice(self.context())

    @admin_privilege_required
    def delete(self):
        return hackathon_manager.delete_hackathon_notice(self.context().id)


class HackathonNoticeListResource(HackathonResource):
    def get(self):
        return hackathon_manager.get_hackathon_notice_list(self.context())
