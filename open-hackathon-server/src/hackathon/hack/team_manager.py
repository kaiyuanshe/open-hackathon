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
from werkzeug.exceptions import Forbidden

sys.path.append("..")

from flask import g

from hackathon import Component, RequiredFeature
from hackathon.database import Team, UserTeamRel, User, Hackathon
from hackathon.hackathon_response import not_found, bad_request, precondition_failed, ok, forbidden
from hackathon.constants import TeamMemberStatus

__all__ = ["TeamManager"]


class TeamManager(Component):
    """Component to manage hackathon teams"""
    user_manager = RequiredFeature("user_manager")
    admin_manager = RequiredFeature("admin_manager")
    template_manager = RequiredFeature("template_manager")

    def get_user_by_teams(self, user_id):
        teams = self.__get_user_teams(user_id)
        team_list = map(lambda x: x._asdict(), teams)

        return team_list

    def get_team_by_name(self, hackathon_id, team_name):
        """ get user's team basic information stored on table 'team' based on team name

        :type hackathon_id: int
        :param hackathon_id: id of hackathon related to the team

        :type team_name: str | unicode
        :param team_name: name of the team

        :rtype: dict
        :return: team's information as a dict if team is found otherwise not_found()
        """
        team = self.__get_team_by_name(hackathon_id, team_name)
        if team:
            return team.dic()
        else:
            return not_found("no such team")

    def get_team_members_by_user(self, hackathon_id, user_id):
        """Get team member list of specific user

        :type hackathon_id: int
        :param hackathon_id: hackathon id

        :type user_id: int
        :param user_id: id of user

        :rtype: dict
        :return: team's information and team's members list if team is found otherwise not_found()
        """
        detail = {}

        team = self.__get_team_by_user(user_id, hackathon_id)
        if team:
            detail["team"] = self.__get_team_by_id(team.id).dic()
            detail["members"] = self.__get_team_members(team)
            return detail
        else:
            return {}

    def get_team_members_by_name(self, hackathon_id, team_name):
        """Get team member list of specific team_name

        :type hackathon_id: int
        :param hackathon_id: hackathon id

        :type team_name: str|unicode
        :param team_name: name of team

        :rtype: dict
        :return: team's information and team's members list if team is found otherwise not_found()
        """

        detail = {}

        team = self.__get_team_by_name(hackathon_id, team_name)
        if team:
            detail["team"] = self.__get_team_by_id(team.id).dic()
            detail["members"] = self.__get_team_members(team)
            return detail
        else:
            return not_found("no such team's members")


    def get_hackathon_team_list(self, hackathon_id, name=None, number=None):
        """Get the team list of selected hackathon

        :type hackathon_id: int
        :param hackathon_id: hackathon id

        :type name: str|unicode
        :param name: name of team. optional

        :type number: int
        :param number: querying condition, return number of teams

        :rtype: list
        :return: a list of team filter by name and number on selected hackathon
        """
        hackathon_team_list = self.db.find_all_objects_by(Team, hackathon_id=hackathon_id)
        hackathon_team_list = map(lambda x: x.dic(), hackathon_team_list)
        if name is not None:
            hackathon_team_list = filter(lambda x: name in x["name"], hackathon_team_list)
        if number is not None:
            hackathon_team_list = hackathon_team_list[0:number]
        return hackathon_team_list

    def create_team(self, kwargs):
        """Create new team by given args.

        user only allow to join or create 1 team. So if user joined or created team before, will be get failed
        when creating new team.

        :type kwargs: dict
        :param kwargs: a dict of required information to create new team

        :rtype: dict
        :return: created team information
        """
        user_team_rel = self.__get_team_by_user(g.user.id, g.hackathon.id)
        if user_team_rel:
            self.log.debug("fail to create team since user is already in some team.")
            return precondition_failed("you must leave the current team first")

        if "team_name" not in kwargs:
            return bad_request("Please provide a team name")

        # check team name to avoid duplicate name
        team_name = kwargs["team_name"]
        if self.__get_team_by_name(g.hackathon.id, team_name):
            return precondition_failed("The team name is existed, please provide a new name")

        team = Team(name=team_name,
                    description=kwargs.get("description"),
                    git_project=kwargs.get("git_project"),
                    logo=kwargs.get("logo"),
                    create_time=self.util.get_now(),
                    update_time=self.util.get_now(),
                    leader_id=g.user.id,
                    hackathon_id=g.hackathon.id)
        self.db.add_object(team)

        user_team_rel = UserTeamRel(join_time=self.util.get_now(),
                                    update_time=self.util.get_now(),
                                    status=TeamMemberStatus.Approved,
                                    hackathon_id=g.hackathon.id,
                                    user_id=g.user.id,
                                    team_id=team.id)
        self.db.add_object(user_team_rel)

        return team.dic()

    def update_team(self, kwargs):
        """Update existing team information

        :type kwargs: dict
        :param kwargs: a dict to store update information for team

        :rtype: dict
        :return: updated team information in a dict
        """
        if "id" not in kwargs:
            return bad_request("Please choose a team to update")

        team = self.__get_team_by_id(kwargs["id"])
        if not team:
            return not_found("team not exists")

        # avoid duplicate team with same names
        if "team_name" in kwargs and kwargs["team_name"] != team.name:
            if self.__get_team_by_name(g.hackathon.id, kwargs["team_name"]):
                return precondition_failed("team with the same name exists already")

        self.__validate_team_permission(g.hackathon.id, team, g.user)
        self.db.update_object(team,
                              name=kwargs.get("team_name", team.name),
                              description=kwargs.get("description", team.description),
                              git_project=kwargs.get("git_project", team.git_project),
                              logo=kwargs.get("logo", team.logo),
                              update_time=self.util.get_now())
        return team.dic()

    def dismiss_team(self, hackathon_id, team_name):
        """Dismiss a team by team leader or hackathon admin

        :type hackathon_id: int
        :param hackathon_id: hackathon id

        :type team_name: str|unicode
        :param team_name: name of the team to dismiss

        :rtype: bool
        :return: if dismiss success, return ok. if not ,return bad request.
        """
        team = self.__get_team_by_name(hackathon_id, team_name)
        if not team:
            return ok()

        self.__validate_team_permission(hackathon_id, team, g.user)

        # delete all team members first
        self.db.delete_all_objects_by(UserTeamRel, team_id=team.id)
        self.db.delete_object(team)
        return ok()

    def join_team(self, hackathon_id, team_name, user):
        """Join a team will create a record on user_team_rel table which status will be 0.

        :type hackathon_id: int
        :param hackathon_id: hackathon id

        :type team_name: str | unicode
        :param team_name: team name

        :type user: User
        :param user: the user to join a team

        :rtype: dict
        :return: if user already joined team or team not exist, return bad request. Else, return a dict of joined
            details.
        """
        if self.db.find_first_object_by(UserTeamRel, hackathon_id=hackathon_id, user_id=g.user.id):
            return precondition_failed("You have joined another team, please quit first.")

        team = self.__get_team_by_name(hackathon_id, team_name)
        if team:
            candidate = UserTeamRel(join_time=self.util.get_now(),
                                    update_time=self.util.get_now(),
                                    status=TeamMemberStatus.Init,
                                    hackathon_id=hackathon_id,
                                    user_id=user.id,
                                    team_id=team.id)
            self.db.add_object(candidate)
            return candidate.dic()
        else:
            return not_found("team not found !")

    def update_team_member_status(self, hackathon_id, team_name, status, operator, candidate_id):
        """ update user's status on selected team. if current user doesn't have permission, return bad request.
        Else, update user's status

        :type hackathon_id: int
        :param hackathon_id: hackathon id

        :type team_name: str|unicode
        :param team_name: team name

        :type status: int
        :param status: the status of the team member, see TeamMemberStatus in constants.py

        :type operator: User
        :param operator: the current login user who trys to change the status of team member

        :type candidate_id: int
        :param candidate_id: the id of candidate who waits for approval

        :rtype: bool
        :return: if update success, return ok. if not , return bad request.
        """
        team = self.__get_team_by_name(hackathon_id, team_name)
        if not team:
            return not_found("team not found")

        self.__validate_team_permission(hackathon_id, team, operator)

        candidate = self.db.find_first_object_by(UserTeamRel, hackathon_id=hackathon_id, user_id=candidate_id)
        if status == TeamMemberStatus.Approved:
            candidate.status = status
            candidate.update_time = self.util.get_now()
            self.db.commit()
            return ok("approved")
        if status == TeamMemberStatus.Denied:
            self.db.delete_object(candidate)
            return ok("Your request has been denied, please rejoin another team.")

    def leave_team(self, hackathon_id, team_name):
        """Leave a team by user

        :type hackathon_id: int
        :param hid: hackathon id

        :type team_name: str|unicode
        :param team_name: team name

        :rtype: bool
        :return: if leave_team success, return ok. if not ,return bad request.
        """

        team = self.__get_team_by_name(hackathon_id, team_name)
        if not team:
            # if team don't exist, do nothing
            return ok()

        # if user is not team leader
        if team.leader_id != g.user.id:
            self.db.delete_all_objects_by(UserTeamRel, hackathon_id=hackathon_id, user_id=g.user.id)
            return ok("You have left the team")

        # if user is team leader
        if len(self.__get_team_members(team)) >= 2:
            return precondition_failed("Please promote a new team leader, before leave team.")
        else:
            return self.dismiss_team(hackathon_id, team_name)

    def kick(self, team_name, candidate_id):
        """ team leader and admin kick some one from team

        :type team_name: str|unicode
        :param tname: team name

        :type candidate_id: int
        :param candidate_id: the candidate to kick off

        :rtype: bool
        :return: if kick success, return ok. if not ,return bad request
        """
        team = self.__get_team_by_name(g.hackathon.id, team_name)
        if not team:
            # if team don't exist, do nothing
            return ok()

        self.__validate_team_permission(g.hackathon.id, team, g.user)
        self.db.delete_all_objects_by(UserTeamRel, team_id=team.id, user_id=candidate_id)
        return ok()

    def promote_leader(self, hackathon_id, team_name, new_leader_id):
        """ team leader promote some one from team to become team leader

        :type hackathon_id: int
        :param hackathon_id: hackathon id

        :type team_name: str|unicode
        :param team_name: team name

        :type new_leader_id: int
        :param new_leader_id: id of user who will become new leader of the team

        :rtype: bool
        :return: if promote success, return ok. if not ,return bad request.
        """

        team = self.__get_team_by_name(hackathon_id, team_name)
        if not team:
            return not_found("team doesn't exist")

        self.__validate_team_permission(hackathon_id, team, g.user)

        # check new leader and old leader in same team
        member = team.user_team_rels.filter_by(user_id=new_leader_id).first()
        if not member:
            return precondition_failed("Please promote someone in the same team.")
        if member.status != TeamMemberStatus.Approved:
            return precondition_failed("The member is not approved yet")

        team.leader_id = new_leader_id
        self.db.commit()
        self.log.debug(team.leader.name + " has been promote to leader.")
        return team.dic()

    def add_template_for_team(self, args):
        """Add template to team of the current user by template name

        template_id must be included in args. Current login user must have a team and HE must be its leader
        """
        if "template_id" not in args:
            return bad_request("template id invalid")

        team = self.__get_team_by_user(g.user.id, g.hackathon.id)
        if not team:
            return precondition_failed("you don't join any team so you cannot add teamplate")

        if team.leader_id != g.user.id:
            return forbidden("team leader required")
        else:
            return self.template_manager.add_template_to_hackathon(args["template_id"], team.id)

    def delete_template_from_team(self, template_id):
        """Delete template from current user's team

        Team should exist and current login user must be the leader
        """
        team = self.__get_team_by_user(g.user.id, g.hackathon.id)
        if not team:
            return precondition_failed("you don't join any team so you cannot add teamplate")

        if team.leader_id != g.user.id:
            return forbidden("team leader required")
        else:
            return self.template_manager.delete_template_from_hackathon(template_id, team.id)

    # ------------------------------ private methods ----------------------------------------

    def __init__(self):
        pass

    def __get_user_teams(self, user_id):
        """Get user teams list and related hackathon display info

        :type user_id: int
        :param user_id: User id to get teams. Cannot be None

        :rtype: list
        :return list of all teams as well as hackathon info
        """

        q = self.db.session().query(UserTeamRel). \
            join(Hackathon, Hackathon.id == UserTeamRel.hackathon_id). \
            join(Team, Team.id == UserTeamRel.team_id). \
            filter(UserTeamRel.user_id == user_id)

        return q.all()


    def __get_team_members(self, team):
        """Get team members list and related user display info

        :type team: Team
        :param team: Team to get members. Cannot be None

        :rtype: list
        :return list of all members as well as user info
        """
        team_members = self.db.find_all_objects_by(UserTeamRel, team_id=team.id)

        def get_info(sql_object):
            r = sql_object.dic()
            r['user'] = self.user_manager.user_display_info(sql_object.user)
            return r

        team_members = map(lambda x: get_info(x), team_members)
        return team_members

    def __get_team_by_id(self, team_id):
        """Get team by its primary key"""
        return self.db.find_first_object_by(Team, id=team_id)

    def __get_team_by_user(self, user_id, hackathon_id):
        """Get User_Team_Rel by user and hackathon

        Since foreign keys are defined in User_Team_Rel, one can access team or user through the return result directly

        :rtype: UserTeamRel
        :return instance of UserTeamRel
        """
        return self.db.find_first_object_by(UserTeamRel, hackathon_id=hackathon_id, user_id=user_id)

    def __get_team_by_name(self, hackathon_id, team_name):
        """ get user's team basic information stored on table 'team' based on team name

        :type hackathon_id: int
        :param hackathon_id: hackathon id for the team

        :type team_name: str|unicode
        :param team_name: name of the team

        :rtype: Team
        :return: instance of Team if team found otherwise None
        """
        return self.db.find_first_object_by(Team, hackathon_id=hackathon_id, name=team_name)

    def __validate_team_permission(self, hackathon_id, team, user):
        """Validate current login user whether has proper right on specific team.

        :type hackathon_id: int
        :param hackathon_id: id of hackathon related to the team

        :type team: Team
        :param team: team to be checked

        :type user: User
        :param user: current login user

        :raise: Forbidden if user is neither team leader, hackathon admin nor super admin
        """
        self.log.debug(
            "validate team permission on hackathon %d and team %s for user %s" % (hackathon_id, team.name, user.id))

        # check if team leader
        if team.leader_id != user.id:
            # check if hackathon admin
            if not self.admin_manager.is_hackathon_admin(hackathon_id, user):
                # check if super admin
                if not self.user_manager.is_super_admin(user):
                    self.log.debug("Access denied for user [%s]%s trying to access team '%s' of hackathon %d " %
                                   (user.id, user.name, team, hackathon_id))
                    raise Forbidden(description="You don't have permission on team '%s'" % team)

        return

    def get_team_by_hackathon(self, hackathon_id):
        return self.db.find_first_object_by(Team, hackathon_id=hackathon_id)

    def get_team_by_user_and_hackathon(self, user, hackathon):
        utrs = self.db.find_all_objects_by(UserTeamRel, user_id=user.id)
        team_ids = map(lambda x: x.team_id, utrs)
        team = self.db.find_first_object(Team, Team.id.in_(team_ids), Team.hackathon_id == hackathon.id)
        return team
