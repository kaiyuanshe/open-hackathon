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

from flask import g

from hackathon import Component
from hackathon.database.models import Team, UserTeamRel, AdminHackathonRel
from hackathon.hackathon_response import ok, access_denied, bad_request


class TeamManager(Component):

    template_manager = RequiredFeature("template_manager")
    user_manager = RequiredFeature("user_manager")
    def __valid_permission__(self, hid, tname, uid):
        if self.db.find_first_object_by(Team, hackathon_id=hid, team_name=tname, leader_id=uid) is not None:
            return True
        elif self.db.find_first_object_by(AdminHackathonRel, hackathon_id=hid, user_id=leader_id) is not None:
            return True
        else:
            return False

    def __getteamid__(self, hid, uid):
        user_team = self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=uid)
        if user_team is not None:
            return user_team.team_id
        else:
            return False

    def get_team_info(self, hid, tname):
        team = self.db.find_first_object_by(Team, hackathon_id=hid, team_name=tname)
        if team is not None:
            return team.dic()

    def get_hackathon_team_list(self, hid, name, number):
        hackathon_team_list = self.db.find_all_objects_by(Team, hackathon_id=hid)
        hackathon_team_list = map(lambda x: x.dic(), hackathon_team_list)
        if name is not None:
            hackathon_team_list = filter(lambda x: name in x["team_name"], hackathon_team_list)
        if number is not None:
            hackathon_team_list = hackathon_team_list[0:number]
        return hackathon_team_list

    def get_team_members_by_team_name(self, uid, tname):
        team= self.db.find_first_objects_by(UserTeamRel, hackathon_id=uid, team_name=tname)
        team_member = self.db.find_all_object_by(UserTeamRel, team_id=team.id)

        def get_info(sql_object):
            r = sql_object.dic()
            r['user'] = self.user_display_info(sql_object.user)
            return r

        team_member = map(lambda x: get_info(x), team_member)
        return team_member

    def get_team_members_by_user(self, hackathon_id, user_id):
        my_team_id = __getteamid__(hackathon_id, user_id)
        if my_team_id is not False:
            my_team_name = self.db.find_first_object_by(Team, team_id=my_team_id)
            return self.get_team_members_by_team_name(hackathon_id, my_team_name)
        else:
            return []

    def create_team(self, **kwargs):
        team = Team(self,
                    name=kwargs["name"],
                    display_name=kwargs["display_name"],
                    description=kwargs["description"],
                    git_project=kwargs["git_project"],
                    logo=kwargs["logo"],
                    create_time=self.util.get_now(),
                    update_time=self.util.get_now(),
                    leader_id=g.user.id,
                    hackathon_id=g.hackathon.id)
        self.db.add_object(team)

        team_id = self.db.find_first_object_by(Team, hackathon_id=g.hackathon.id, leader_id=g.user.id)
        userteamrel = UserTeamRel(self,
                                  join_time=self.util.get_now(),
                                  update_time=self.util.get_now(),
                                  status=1,
                                  hackathon_id=g.hackathon.id,
                                  user_id=g.user.id,
                                  team_id=team_id.team_id)
        self.db.add_object(userteamrel)
        return ok("Team has created")
    def join_team(self, hid, tname, uid):
        team_id = self.db.find_first_object_by(Team, hackathon_id=hid, team_name=tname)
        candidate = UserTeamRel(self,
                                join_time=self.util.get_now(),
                                update_time=self.util.get_now(),
                                status=0,
                                hackathon_id=hid,
                                user_id=uid,
                                team_id=team_id.team_id)
        self.db.add_object(candidate)
        return ok("Wait team leader approve")
    def apply_team_manage(self, hid, tname, status, leader_id, candidate_id):
        if __valid_permission__(hid,tname,leader_id) is not False:
            candidate = self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=candidate_id)
            candidate.status = status
            candidate.update_time=self.util.get_now()
            self.db.commit()
            return ok("Approved")


    def leave_team(self, hid, tname,leader_id candidate_id):
        def leave(self, hid, candidate_id):
            candidate = self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=candidate_id)
            self.db.delete_object(candidate)
            return ok("You have left the team")

        # if user is not team leader
        if self.db.find_first_object_by(Team, hackathon_id=hid, team_name=tname, leader_id=candidate_id) is None:
            return leave(hid, candidate_id)

        # if user is team leader
        elif self.db.find_first_object_by(Team, hackathon_id=hid, team_name=tname, leader_id=candidate_id) is not None:
            team_members = self.get_team_members_by_user(hid,candidate_id)
            if len(team_members)>=2: return bad_request("Please promo a new team leader, before leave team.")
            else: return bad_request("You are last one of team, please use \"Dismiss\" button to dismiss team.")

        # if user is hackathon admin
        elif self.db.find_first_object_by(AdminHackathonRel, hackathon_id=hid, user_id=leader_id) is not None:
            return leave(hid, candidate_id)

        elif self.is_super_admin(leader_id) is True:
            return leave(hid, tname, candidate_id)

    def promo_leader(self, hid, tname, new_uid, old_uid):
        leader = self.db.find_first_object_by(Team, hackathon_id=hid, team_name=tname, leader_id=old_uid)
        leader.leader_id = new_uid
        self.db.commit()

    def dismiss_team(self, hid, tname):
        if __valid_permission__(hid,tname, g.user.id) is not False:
            team = self.db.find_first_object_by(Team, hackathon_id=hid, team_name=tname)
            members = self.db.find_all_objects_order_by(UserTeamRel, Team_id=team.id)
            lambda x: self.db.delete_object(x), members
            self.db.delete_object(team)



    def add_template(self, template_name):
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

