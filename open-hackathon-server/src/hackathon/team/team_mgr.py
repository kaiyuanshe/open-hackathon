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

from hackathon import Component, RequiredFeature
from hackathon.database.models import Team, UserTeamRel, AdminHackathonRel, User
from hackathon.hackathon_response import ok, forbidden, bad_request, not_found, internal_server_error
from hackathon.constants import TeamMemberStatus


class TeamManager(Component):
    template_manager = RequiredFeature("template_manager")
    user_manager = RequiredFeature("user_manager")

    def get_team_info(self, hid, tname):
        """ get user's team basic information stored on table 'team' based on team name

        :type hid: int
        :param hid: key to store hackathon id

        :type tname: str|unicode
        :param tname: key to store team name

        :rtype: dict
        :return: team's information as a dict
        """
        team = self.db.find_first_object_by(Team, hackathon_id=hid, name=tname)
        if team is not None:
            return team.dic()
        else:
            return not_found("no such team")

    def get_hackathon_team_list(self, hid, name=None, number=None):
        """ get the team list of selected hackathon

        :type hid: int
        :param hid: the key to store hackathon id

        :type name: str|unicode
        :param name: querying condition, return selected team name list

        :type number: int
        :param number: querying condition, return number of teams

        :rtype: list
        :return: a list of team filter by name and number on selected hackathon
        """
        hackathon_team_list = self.db.find_all_objects_by(Team, hackathon_id=hid)
        hackathon_team_list = map(lambda x: x.dic(), hackathon_team_list)
        if name is not None:
            hackathon_team_list = filter(lambda x: name in x["name"], hackathon_team_list)
        if number is not None:
            hackathon_team_list = hackathon_team_list[0:number]
        return hackathon_team_list

    def get_team_members_by_user(self, hackathon_id, user_id):
        """ get given user's team member

        :type hackathon_id: int
        :param hackathon_id: the key to store hackathon id

        :type user_id: int
        :param user_id: the key to store user id

        :rtype: list
        :return: a dict of user's team member
        """

        my_team = self.__get_team(hackathon_id, user_id)
        if my_team is not None:
            team_member = self.db.find_all_objects_by(UserTeamRel, team_id=my_team.team_id)

            def get_info(sql_object):
                r = sql_object.dic()
                r['user'] = self.user_manager.user_display_info(sql_object.user)
                return r

            team_member = map(lambda x: get_info(x), team_member)
            return team_member
        else:
            return []

    def create_team(self, kwargs):
        """ create new team by given args.
            user only allow to join or create 1 team. So if user joined or created team before, will be get failed
            when creating new team.

        :type kwargs: dict
        :param kwargs: a dict of required information to create new team

        :rtype: dict
        :return: return created team information
        """
        team = self.db.find_first_object_by(UserTeamRel, hackathon_id=g.hackathon.id, user_id=g.user.id)
        if team is not None:
            return self.db.find_first_object_by(Team, id=team.team_id).dic()
        if "team_name" not in kwargs.keys():
            return bad_request("Please provide a team name")
        # check team name to avoid duplicate name
        if self.db.find_first_object_by(Team, name=kwargs["team_name"], hackathon_id=g.hackathon.id):
            return bad_request("The team name is existed, please provide a new name")
        description = kwargs["description"] if "description" in kwargs else ""
        git_project = kwargs["git_project"] if "git_project" in kwargs else ""
        logo = kwargs["logo"] if "logo" in kwargs else ""
        team = Team(name=kwargs["team_name"],
                    description=description,
                    git_project=git_project,
                    logo=logo,
                    create_time=self.util.get_now(),
                    update_time=self.util.get_now(),
                    leader_id=g.user.id,
                    hackathon_id=g.hackathon.id)
        self.db.add_object(team)

        userteamrel = UserTeamRel(join_time=self.util.get_now(),
                                  update_time=self.util.get_now(),
                                  status=TeamMemberStatus.Allow,
                                  hackathon_id=g.hackathon.id,
                                  user_id=g.user.id,
                                  team_id=team.id)
        self.db.add_object(userteamrel)
        return team.dic()

    def update_team(self, kwargs):
        """ use to update team information

        :type kwargs: kwargs
        :param kwargs: a dict to store update information for team

        :rtype: dict
        :return:  return updated team information in a dict
        """
        if "team_name" in kwargs.keys():
            team_name = kwargs["team_name"]
            team = self.db.find_first_object_by(Team, hackathon_id=g.hackathon.id, name=team_name)
            if self.__validate_permission(g.hackathon.id, team.name, g.user):
                description = kwargs["description"] if "description" in kwargs else team.description
                git_project = kwargs["git_project"] if "git_project" in kwargs else team.git_project
                logo = kwargs["logo"] if "logo" in kwargs else team.logo
                self.db.update_object(team,
                                      name=name,
                                      description=description,
                                      git_project=git_project,
                                      logo=logo,
                                      update_time=self.util.get_now())
                return team.dic()
            else:
                return forbidden("You don't have permission")
        else:
            return bad_request("Please choose a team to update")

    def join_team(self, hid, tname, user):
        """ user join a team will create a record on user_team_rel table which status will be 0.
        :type hid: int
        :param hid: the key to store hackathon id

        :type tname: str | unicode
        :param tname: the key to store team name

        :type user: User
        :param user: User object which wants join the team

        :rtype: dict
        :return: if user already joined team or team not exist, return bad request. Else, return a dict of joined
            details.
        """
        if self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=g.user.id):
            return bad_request("You have joined another team, please quit first.")

        team = self.db.find_first_object_by(Team, hackathon_id=hid, name=tname)
        if team is not None:
            candidate = UserTeamRel(join_time=self.util.get_now(),
                                    update_time=self.util.get_now(),
                                    status=TeamMemberStatus.Init,
                                    hackathon_id=hid,
                                    user_id=user.id,
                                    team_id=team.id)
            self.db.add_object(candidate)
            return candidate.dic()
        else:
            return bad_request("team not found !")

    def update_status(self, hid, tname, status, user, candidate_id):
        """ update user's status on selected team. if current user doesn't have permission, return bad request.
        Else, update user's status

        :type hid: int
        :param hid: the key to store hackathon id

        :type tname: str|unicode
        :param tname: the key to store team name

        :type status: int
        :param status: the key to indicate the status of the team

        :type user: User
        :param user: the current log in user

        :type candidate_id: int
        :param candidate_id: the candidate wait for approve

        :rtype: bool
        :return: if update success, return ok. if not , return bad request.
        """
        if self.__validate_permission(hid, tname, user) is not False:
            candidate = self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=candidate_id)
            if status == 1:
                candidate.status = status
                candidate.update_time = self.util.get_now()
                self.db.commit()
                return ok("Your request has been approved")
            if status == 2:
                self.db.delete_object(candidate)
                return ok("Your request has been denied, please rejoin another team.")

    def leave_team(self, hid, tname):
        """ team member leave team

        :type hid: int
        :param hid: the key to store hackathon id

        :type tname: str|unicode
        :param tname: the key to store team name

        :rtype: bool
        :return: if leave_team success, return ok. if not ,return bad request.
        """

        # if user is not team leader
        if self.db.find_first_object_by(Team, hackathon_id=hid, name=tname, leader_id=g.user.id) is None:
            candidate = self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=candidate_id)
            self.db.delete_object(candidate)
            return ok("You have left the team")

        # if user is team leader
        elif self.db.find_first_object_by(Team, hackathon_id=hid, name=tname, leader_id=g.user.id) is not None:
            team_members = self.get_team_members_by_user(hid, g.user.id)
            if len(team_members) >= 2:
                return bad_request("Please promo a new team leader, before leave team.")
            else:
                return bad_request("You are last one of team, please use \"Dismiss\" button to dismiss team.")

    def kick(self, tname, candidate_id):
        """ team leader and admin kick some one from team

        :type tname: str|unicode
        :param tname: the key to store team name

        :type candidate_id: int
        :param candidate_id: the candidate wait for approve

        :rtype: bool
        :return: if kick success, return ok. if not ,return bad request
        """
        if self.__validate_permission(g.hackathon.id, tname, g.user) is not False:
            team = self.db.find_first_object_by(Team, hackation_id=g.hackathon.id, name=tname)
            candidate_record = self.db.find_first_object_by(UserTeamRel, team_id=team.id, user_id=candidate_id)
            if candidate_record is not None:
                self.log.debug("User" + candidate_id.user_team_rels.name + "has been kicked from" + team.name)
                self.db.delete_object(candidate_record)
                return ok("kicked")

    def promote_leader(self, hid, tname, candidate_id):
        """ team leader promote some one from team to become team leader

        :type hid: int
        :param hid: the key to store hackathon id

        :type tname: str|unicode
        :param tname: the key to store team name

        :type candidate_id: int
        :param candidate_id: the candidate wait for become leader

        :rtype: bool
        :return: if promote success, return ok. if not ,return bad request.
        """
        # check permission
        if self.__validate_permission(hid, tname, g.user):
            # check new leader and old leader in same team
            team = self.db.find_first_object_by(Team, hackathon_id=hid, name=tname)
            leader_id = team.leader_id
            team_member = team.user_team_rels.all()
            team_member_id = map(lambda x: x.user_id, team_member)
            if candidate_id in team_member_id and leader_id in team_member_id:
                team.leader_id = candidate_id
                self.log.debug(team.leader.name + " has been promote to leader.")
                self.db.commit()
                return team.dic()
            else:
                return bad_request("Please promote someone in the same team.")

    def dismiss_team(self, hid, tname):
        """ team leader and admin dismiss team

        :type hid: int
        :param hid: the key to store hackathon id

        :type tname: str|unicode
        :param tname: the key to store team name

        :rtype: bool
        :return: if dismiss success, return ok. if not ,return bad request.
        """
        if self.__validate_permission(hid, tname, g.user) is not False:
            team = self.db.find_first_object_by(Team, hackathon_id=hid, name=tname)
            self.db.delete_all_objects_by(UserTeamRel, team_id=team.id)
            self.log.debug(g.user.name + " has dismissed team: " + tname)
            self.db.delete_object(team)
            return ok("you have dismissed team")

    def get_team_by_user_and_hackathon(self, user, hackathon):
        utrs = self.db.find_all_objects_by(UserTeamRel, user_id=user.id)
        team_ids = map(lambda x: x.team_id, utrs)
        team = self.db.find_first_object(Team, Team.id.in_(team_ids), Team.hackathon_id == hackathon.id)
        return team

    def team_leader_add_template(self, template_name):
        team = self.get_team_by_user_and_hackathon(g.user, g.hackathon)
        if team is None or team.leader_id != g.user.id:
            return forbidden("team leader required")
        else:
            return self.template_manager.add_template_to_hackathon(template_name, team.id)

    def team_leader_delete_template(self, template_id):
        team = self.get_team_by_user_and_hackathon(g.user, g.hackathon)
        if team is None or team.leader_id != g.user.id:
            return forbidden("team leader required")
        else:
            return self.template_manager.delete_template_from_hackathon(template_id, team.id)


------------------------------------------------------------------------------------------------------------------------


def __validate_permission(self, hid, tname, user):
    """ validate the current user have certain permission to perform managenment actions

    :type: hid: int
    :param hid: key to store hackathon id

    :type: tname: str|unicode
    :param tname: key to store team name

    :type: user: User
    :param user: the selected user to examine permission

    :rtype: bool
    :return: True or False. If user has permission, return True. Else, return false
    """
    # check if team leader
    if self.db.find_first_object_by(Team, hackathon_id=hid, name=tname, leader_id=user.id) is not None:
        return True
    # check if hackathon admin
    elif self.db.find_first_object_by(AdminHackathonRel, hackathon_id=hid, user_id=user.id) is not None:
        return True
    # check if super admin
    elif self.user_manager.is_super_admin(user) is True:
        return True
    else:
        return False


def __get_team(self, hid, uid):
    """ get the given user' team

    :type hid: int
    :param hid: the key to store hackathon id

    :type uid: int
    :param uid: the key to store user id

    :rtype: UserTeamRel
    :return:get user's team on selected hackathon
    """
    return self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=uid)
