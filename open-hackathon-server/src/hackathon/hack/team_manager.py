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
from hackathon.database import Team, UserTeamRel, User, Hackathon, TeamScore, TeamShow
from hackathon.hackathon_response import not_found, bad_request, precondition_failed, ok, forbidden
from hackathon.constants import TeamMemberStatus, Team_Show_Type

__all__ = ["TeamManager"]


class TeamManager(Component):
    """Component to manage hackathon teams"""
    user_manager = RequiredFeature("user_manager")
    admin_manager = RequiredFeature("admin_manager")
    register_manager = RequiredFeature("register_manager")
    hackathon_template_manager = RequiredFeature("hackathon_template_manager")

    def get_team_by_id(self, team_id):
        team = self.__get_team_by_id(team_id)

        # check whether it's anonymous user or not
        user = None
        if self.user_manager.validate_login():
            user = g.user

        if team:
            return self.__team_detail(team, user)
        else:
            return not_found()

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

        # check whether it's anonymous user or not
        user = None
        if self.user_manager.validate_login():
            user = g.user

        if team:
            return self.__team_detail(team, user)
        else:
            return not_found("no such team")

    def get_team_members(self, team_id):
        """Get team member list of specific team

        :rtype: dict
        :return: team's information and team's members list if team is found otherwise not_found()
        """
        rels = self.db.find_all_objects_by(UserTeamRel, team_id=team_id)

        def sub(t):
            m = t.dic()
            m["user"] = self.user_manager.user_display_info(t.user)
            return m

        return map(lambda t: sub(t), rels)

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
        if name is not None:
            hackathon_team_list = filter(lambda t: name in t.name, hackathon_team_list)
        if number is not None:
            hackathon_team_list = hackathon_team_list[0:number]

        # check whether it's anonymous user or not
        user = None
        if self.user_manager.validate_login():
            user = g.user

        hackathon_team_list = map(lambda x: self.__team_detail(x, user), hackathon_team_list)
        return hackathon_team_list

    def create_default_team(self, hackathon, user):
        """Create a default new team for user after registration.

        Use user name as team name by default. Append user id in case user name is duplicate
        """
        user_team_rel = self.__get_valid_team_by_user(user.id, hackathon.id)
        if user_team_rel:
            self.log.debug("fail to create team since user is already in some team.")
            return precondition_failed("you must leave the current team first")

        team_name = self.__generate_team_name(hackathon, user)
        team = Team(name=team_name,
                    leader_id=user.id,
                    hackathon_id=hackathon.id)
        self.db.add_object(team)

        user_team_rel = UserTeamRel(join_time=self.util.get_now(),
                                    status=TeamMemberStatus.Approved,
                                    hackathon_id=hackathon.id,
                                    user_id=user.id,
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
        team = self.__get_team_by_id(kwargs["id"])
        if not team:
            return not_found("team not exists")

        # avoid duplicate team with same names
        if "name" in kwargs and kwargs["name"] != team.name:
            if self.__get_team_by_name(g.hackathon.id, kwargs["name"]):
                return precondition_failed("team with the same name exists already")

        self.__validate_team_permission(g.hackathon.id, team, g.user)
        self.db.update_object(team,
                              name=kwargs.get("name", team.name),
                              description=kwargs.get("description", team.description),
                              logo=kwargs.get("logo", team.logo),
                              update_time=self.util.get_now())
        return self.__team_detail(team)

    def dismiss_team(self, operator, team_id):
        """Dismiss a team by team leader or hackathon admin

        :rtype: bool
        :return: if dismiss success, return ok. if not ,return bad request.
        """
        team = self.__get_team_by_id(team_id)
        if not team:
            return ok()

        hackathon = team.hackathon
        self.__validate_team_permission(hackathon.id, team, operator)

        members = self.db.find_all_objects_by(UserTeamRel, team_id=team.id, status=TeamMemberStatus.Approved)
        member_ids = [m.user for m in members]

        # delete all team members first
        self.db.delete_all_objects_by(UserTeamRel, team_id=team.id)
        self.db.delete_object(team)

        for u in member_ids:
            self.create_default_team(hackathon, u)

        return ok()

    def join_team(self, user, team_id):
        """Join a team will create a record on user_team_rel table which status will be 0.

        :type user: User
        :param user: the user to join a team

        :rtype: dict
        :return: if user already joined team or team not exist, return bad request. Else, return a dict of joined
            details.
        """
        if self.db.find_first_object_by(UserTeamRel, user_id=user.id, team_id=team_id):
            return ok("You already joined this team.")

        team = self.__get_team_by_id(team_id)
        if not team:
            return not_found()

        cur_team = self.__get_valid_team_by_user(user.id, team.hackathon_id)
        if cur_team and cur_team.team.user_team_rels.count() > 1:
            return precondition_failed("Team leader cannot join another team for team member count greater than 1")

        if not self.register_manager.is_user_registered(user.id, team.hackathon):
            return precondition_failed("user not registerd")

        candidate = UserTeamRel(join_time=self.util.get_now(),
                                update_time=self.util.get_now(),
                                status=TeamMemberStatus.Init,
                                hackathon_id=team.hackathon.id,
                                user_id=user.id,
                                team_id=team.id)
        self.db.add_object(candidate)
        return candidate.dic()

    def update_team_member_status(self, operator, user_team_rel_id, status):
        """ update user's status on selected team. if current user doesn't have permission, return bad request.
        Else, update user's status

        :type status: int
        :param status: the status of the team member, see TeamMemberStatus in constants.py

        :rtype: bool
        :return: if update success, return ok. if not , return bad request.
        """
        rel = self.db.find_first_object_by(UserTeamRel, id=user_team_rel_id)
        if not rel:
            return not_found()

        team = rel.team
        self.__validate_team_permission(rel.hackathon_id, team, operator)

        if rel.user_id == team.leader_id:
            return precondition_failed("cannot update status of team leader")

        if status == TeamMemberStatus.Approved:
            # disable previous team first
            self.db.delete_all_objects_by(UserTeamRel,
                                          hackathon_id=rel.hackathon_id,
                                          user_id=rel.user_id,
                                          status=TeamMemberStatus.Approved)
            self.db.delete_all_objects_by(Team, hackathon_id=rel.hackathon_id, leader_id=rel.user_id)

            rel.status = TeamMemberStatus.Approved
            rel.update_time = self.util.get_now()
            self.db.commit()
            return ok("approved")
        if status == TeamMemberStatus.Denied:
            user = rel.user
            hackathon = rel.hackathon
            self.db.delete_object(rel)
            self.create_default_team(hackathon, user)
            return ok("Your request has been denied, please rejoin another team.")

    def kick_or_leave(self, operator, team_id, user_id):
        rel = self.db.find_first_object_by(UserTeamRel, team_id=team_id, user_id=user_id)
        if not rel:
            return not_found()

        team = rel.team
        hackathon = rel.hackathon
        user = rel.user
        if team.leader_id == rel.user_id:  # if the user to be leaved or kicked is team leader
            return precondition_failed("leader cannot leave team")

        if operator.id == rel.user_id:  # leave team
            self.db.delete_object(rel)
            self.db.commit()
            self.create_default_team(rel.hackathon, rel.user)
        else:  # kick somebody else
            self.__validate_team_permission(hackathon.id, team, operator)
            self.db.delete_object(rel)
            self.create_default_team(hackathon, user)

        return ok()

    def add_template_for_team(self, args):
        """Add template to team of the current user by template name

        template_id must be included in args. Current login user must have a team and HE must be its leader
        """
        if "template_id" not in args:
            return bad_request("template id invalid")

        team = self.__get_valid_team_by_user(g.user.id, g.hackathon.id)
        if not team:
            return precondition_failed("you don't join any team so you cannot add teamplate")

        if team.leader_id != g.user.id:
            return forbidden("team leader required")
        else:
            return self.hackathon_template_manager.add_template_to_hackathon(args["template_id"], team.id)

    def delete_template_from_team(self, template_id):
        """Delete template from current user's team

        Team should exist and current login user must be the leader
        """
        team = self.__get_valid_team_by_user(g.user.id, g.hackathon.id)
        if not team:
            return precondition_failed("you don't join any team so you cannot add teamplate")

        if team.leader_id != g.user.id:
            return forbidden("team leader required")
        else:
            return self.hackathon_template_manager.delete_template_from_hackathon(template_id, team.id)

    def get_team_by_user_and_hackathon(self, user, hackathon):
        utrs = self.db.find_first_object_by(UserTeamRel, user_id=user.id, hackathon_id=hackathon.id)
        return utrs.team if utrs else None

    def score_team(self, judge, ctx):
        team = self.__get_team_by_id(ctx.team_id)
        if not team:
            return not_found("team not found")

        if not self.admin_manager.is_hackathon_admin(team.hackathon_id, judge.id):
            return forbidden()

        score = self.db.find_first_object_by(TeamScore, team_id=team.id, judge_id=judge.id)
        if score:
            score.score = ctx.score
            score.reason = ctx.get("reason")
            score.update_time = self.util.get_now()
            self.db.commit()
        else:
            score = TeamScore(score=ctx.score, team_id=team.id, judge_id=judge.id, reason=ctx.get("reason"))
            self.db.add_object(score)

        return self.get_score(judge, team.id)

    def get_score(self, user, team_id):
        team = self.__get_team_by_id(team_id)
        if not team:
            return not_found("team not found")

        if not self.admin_manager.is_hackathon_admin(team.hackathon_id, user.id):
            return {}

        scores = self.db.find_all_objects_by(TeamScore, team_id=team_id)
        resp = {
            "all": [s.dic() for s in scores]
        }
        my = filter(lambda sc: sc.judge_id == user.id, scores)
        if len(my):
            resp["my"] = my[0].dic()

        return resp

    def add_team_show(self, user, context):
        team = self.__get_team_by_id(context.team_id)
        if not team:
            return not_found()

        self.__validate_team_permission(team.hackathon_id, team, user)
        show = TeamShow(
            note=context.get("note"),
            type=context.type,
            uri=context.uri,
            team_id=context.team_id
        )
        self.db.add_object(show)
        return show.dic()

    def delete_team_show(self, user, show_id):
        show = self.db.find_first_object_by(TeamShow, id=show_id)
        if show:
            self.__validate_team_permission(show.team.hackathon_id, show.team, user)
            self.db.delete_object(show)
            self.db.commit()

        return ok()

    def get_team_show_list(self, team_id):
        show_list = self.db.find_all_objects_by(TeamShow, team_id=team_id)
        return [s.dic() for s in show_list]

    def get_team_source_code(self, team_id):
        return self.db.find_first_object_by(TeamShow, team_id=team_id, type=Team_Show_Type.SourceCode)

    def __init__(self):
        pass

    def __team_detail(self, team, user=None):
        resp = team.dic()
        resp["leader"] = self.user_manager.user_display_info(team.leader)
        resp["member_count"] = team.user_team_rels.filter_by(status=TeamMemberStatus.Approved).count()
        resp["is_admin"] = False
        resp["is_leader"] = False
        resp["is_member"] = False
        if user:
            resp["is_admin"] = self.admin_manager.is_hackathon_admin(team.hackathon_id, user.id)
            resp["is_leader"] = team.leader_id == user.id
            rel = self.db.find_first_object_by(UserTeamRel, team_id=team.id, user_id=user.id)
            resp["is_member"] = rel is not None

        return resp

    def __generate_team_name(self, hackathon, user):
        """Generate a default team name by user name. It can be updated later by team leader"""
        team_name = user.name
        if self.db.find_first_object_by(Team, hackathon_id=hackathon.id, name=team_name):
            team_name = "%s (%s)" % (user.name, user.id)
        return team_name

    def __get_user_teams(self, user_id):
        """Get all teams of specific and related hackathon display info

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

    def __get_valid_team_by_user(self, user_id, hackathon_id):
        """Get valid User_Team_Rel by user and hackathon

        "valid" means user is approved. There might be other records where status=Init
        Since foreign keys are defined in User_Team_Rel, one can access team or user through the return result directly

        :rtype: UserTeamRel
        :return instance of UserTeamRel
        """
        return self.db.find_first_object_by(UserTeamRel,
                                            hackathon_id=hackathon_id,
                                            user_id=user_id,
                                            status=TeamMemberStatus.Approved)

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
            if not self.admin_manager.is_hackathon_admin(hackathon_id, user.id):
                # check if super admin
                if not self.user_manager.is_super_admin(user):
                    self.log.debug("Access denied for user [%s]%s trying to access team '%s' of hackathon %d " %
                                   (user.id, user.name, team, hackathon_id))
                    raise Forbidden(description="You don't have permission on team '%s'" % team)

        return
