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
from hackathon.database.models import UserTeamRel, Team
from flask import g
from hackathon import Component, RequiredFeature
from hackathon.hackathon_response import access_denied, bad_request, not_found, internal_server_error, ok


class TeamManager(Component):

    template_manager = RequiredFeature("template_manager")

    def get_team_by_id(self, team_id):
        return self.db.find_first_object_by(Team, id=team_id)

    def get_team_by_name(self, team_name):
        return self.db.find_first_object_by(Team, name=team_name)

    def get_team_by_user_and_hackathon(self, user, hackathon):
        utrs = self.db.find_all_objects_by(UserTeamRel, user_id=user.id)
        team_ids = map(lambda x: x.team_id, utrs)
        team = self.db.find_first_object(Team, Team.id.in_(team_ids), Team.hackathon_id == hackathon.id)
        return team

    def team_leader_add_template(self, template_name):
        team = self.get_team_by_user_and_hackathon(g.user, g.hackathon)
        if team is None or team.leader_id != g.user.id:
            return access_denied("team leader required")
        else:
            return self.template_manager.add_template_to_hackathon(template_name, team.id)

    def team_leader_delete_template(self, template_id):
        team = self.get_team_by_user_and_hackathon(g.user, g.hackathon)
        if team is None or team.leader_id != g.user.id:
            return access_denied("team leader required")
        else:
            return self.template_manager.delete_template_from_hackathon(template_id, team.id)

    def leader_approve_user(self, args):
        return_status, return_info = self.__check_approve_user_args(args)
        if not return_status:
            return return_info
        utr = return_info
        status = args['status']
        try:
            self.db.update_object(utr, status=status)
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("update user_team_rel record faild")

    def leader_kick_user(self, args):
        return_status, return_info = self.__check_leader_kick_user_args(args)
        if not return_status:
            return return_info
        utr = return_info
        try:
            self.db.delete_object(utr)
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("delete user_team_rel record faild")

    def leader_dismiss_team(self, args):
        return_status, return_info = self.__check_team_leader_args(args)
        if not return_status:
            return return_info
        team = return_info


    def user_leave_team(self, args):
        return_status, return_info = self.__check_team_leader_args(args)
        if not return_status:
            return return_info
        utr = return_info
        try:
            self.db.delete_object(utr)
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("delete user_team_rel record faild")

    #----------------------------helper functions---------------------------#

    def __check_team_leader_args(self, args):
        if 'team_id' not in args:
            return False, bad_request("team_id invalid")

        team = self.get_team_by_id(args['team_id'])
        if team is None:
            return False, not_found("team does not exist")

        if team.leader_id != g.user.id:
            return False, access_denied("team leader required")

        return True, team

    def __check_approve_user_args(self, args):
        return_status, return_info = self.__check_team_leader_args(args)
        if not return_status:
            return return_status, return_info

        if 'user_id' not in args:
            return False, bad_request("user_id invalid")

        if 'status' not in args:
            return False, bad_request("status invalid")

        utr = self.db.find_first_object_by(UserTeamRel, team_id=args['team_id'], user_id=['user_id'])
        if utr is None:
           return False, not_found("user_team_rel does not exist")

        return True, utr

    def __check_leader_kick_user_args(self, args):
        return_status, return_info = self.__check_team_leader_args(args)
        if not return_status:
            return return_status, return_info

        if 'user_id' not in args:
            return False, bad_request("user_id invalid")

        utr = self.db.find_first_object_by(UserTeamRel, team_id=args['team_id'], user_id=['user_id'])
        if utr is None:
           return False, ok("user_team_rel already removed")

        return True, utr

    def __check_user_leave_team_args(self, args):
        if 'team_id' not in args:
            return False, bad_request("team_id invalid")

        team = self.get_team_by_id(args['team_id'])
        if team is None:
            return False, ok("team already dismiss")

        utr = self.db.find_first_object_by(UserTeamRel, team_id=args['team_id'], user_id=g.user.id)
        if utr is None:
           return False, ok("user_team_rel already removed")

        return True, utr