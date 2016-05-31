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

import uuid
import time
from flask import g
import threading
from mongoengine import Q, ValidationError
from os.path import realpath, abspath, dirname

from hackathon import Component, RequiredFeature
from hackathon.hmongo.models import Team, TeamMember, TeamScore, TeamWork, Hackathon, UserHackathon, to_dic
from hackathon.hackathon_response import not_found, bad_request, precondition_failed, ok, forbidden
from hackathon.constants import TEAM_MEMBER_STATUS, TEAM_SHOW_TYPE, HACK_USER_TYPE, HACKATHON_CONFIG

__all__ = ["TeamManager"]
hack_manager = RequiredFeature("hackathon_manager")


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
            # TODO: refine: dereference member users is not necessary
            return self.__team_detail(team, user)
        else:
            return not_found()

    def get_my_current_team(self, hackathon, user):
        team = self.__get_valid_team_by_user(user.id, hackathon.id)
        return self.__team_detail(team, user) if team else not_found("user has no team",
                                                                     friendly_message="组队异常，请联系管理员!")

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
        try:
            team = Team.objects(id=team_id).first()
        except ValidationError:
            return None

        if not team:
            return None

        def sub(t):
            m = to_dic(t)
            m["user"] = self.user_manager.user_display_info(t.user)
            return m

        return [sub(t) for t in team.members]

    def get_hackathon_team_list(self, hackathon_id, name=None, number=None):
        """Get the team list of selected hackathon

        :type hackathon_id: string or object_id
        :param hackathon_id: hackathon id

        :type name: str|unicode
        :param name: name of team. optional

        :type number: int
        :param number: querying condition, return number of teams

        :rtype: list
        :return: a list of team filter by name and number on selected hackathon
        """
        query = Q(hackathon=hackathon_id)
        if name is not None:
            query &= Q(name__icontains=name)

        try:
            teams = Team.objects(query).order_by('name')[:number]
        except ValidationError:
            return []

        # check whether it's anonymous user or not
        user = None
        if self.user_manager.validate_login():
            user = g.user

        def get_team(team):
            teamDic = team.dic()
            teamDic['leader'] = {
                'id': str(team.leader.id),
                'name': team.leader.name,
                'nickname': team.leader.nickname,
                'avatar_url': team.leader.avatar_url
            }
            teamDic['cover'] = teamDic.get('cover', '')
            teamDic['project_name'] = teamDic.get('project_name', '')
            teamDic['dev_plan'] = teamDic.get('dev_plan', '')
            teamDic['works'] = teamDic.get('works', '')
            [teamDic.pop(key, None) for key in
             ['assets', 'azure_keys', 'scores', 'templates', 'hackathon']]
            teamDic["member_count"] = team.members.filter(status=TEAM_MEMBER_STATUS.APPROVED).count()

            def sub(t):
                m = to_dic(t)
                m["user"] = self.user_manager.user_display_info(t.user)
                return m

            teamDic["members"] = [sub(t) for t in team.members]
            return teamDic

        return [get_team(x) for x in teams]

    def create_default_team(self, hackathon, user):
        """Create a default new team for user after registration.

        Use user name as team name by default. Append user id in case user name is duplicate
        """
        user_team = self.__get_valid_team_by_user(user.id, hackathon.id)
        if user_team:
            self.log.debug("fail to create team since user is already in some team.")
            return precondition_failed("you must leave the current team first")

        team_name = self.__generate_team_name(hackathon, user)
        team_member = TeamMember(join_time=self.util.get_now(),
                                 status=TEAM_MEMBER_STATUS.APPROVED,
                                 user=user)
        team = Team(name=team_name,
                    leader=user,
                    logo=user.avatar_url,
                    hackathon=hackathon,
                    members=[team_member])
        team.save()

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

        # hackathon.modify(**update_items)
        # team.name = kwargs.get("name", team.name)
        # team.description = kwargs.get("description", team.description)
        # team.logo = kwargs.get("logo", team.logo)

        kwargs.pop('id', None)  # id should not be included
        team.modify(**kwargs)
        team.update_time = self.util.get_now()
        team.save()

        if "dev_plan" in kwargs and kwargs["dev_plan"] and not kwargs["dev_plan"] == "" \
                and team.hackathon.config.get(HACKATHON_CONFIG.DEV_PLAN_REQUIRED, False):
            t = threading.Thread(target=self.__email_notify_dev_plan_submitted, args=(team,))
            t.setDaemon(True)
            t.start()

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

        members = team.members
        member_users = [m.user for m in members]

        # TODO: transcation?
        team.delete()

        for u in member_users:
            self.create_default_team(hackathon, u)

        return ok()

    def quit_team_forcedly(self, team, user):
        """
        The operator(admin or superadmin) forces a user(team leader or other members) to quit a team.
        If the user is the only member of the team, the team will be deleted.
        Else if the user is the leader of a team with several members, the team will be decomposed into several
        new teams.
        Else if the user is not the leader of a team with several members, just the user quits the team.

        :rtype: bool
        :return: if dismiss success, return ok. if not ,return bad request.
        """

        # here we don't check whether the operator has the permission,
        if not team.members or len(team.members) == 0:
            self.log.warn("this team doesn't have any members")
            return ok()
        member_users = [m.user for m in team.members if m.status == TEAM_MEMBER_STATUS.APPROVED]

        num_team_members = len(member_users)
        hackathon = team.hackathon
        if num_team_members > 1:
            if team.leader == user:
                team.delete()
                for u in member_users:
                    if u.id != user.id:
                        self.create_default_team(hackathon, u)
            else:
                Team.objects(id=team.id).update_one(pull__members__user=user)
        else:
            # num_team_members == 1
            team.delete()

        return ok()

    def join_team(self, user, team_id):
        """Join a team will create a record on user_team_rel table which status will be 0.

        :type user: User

        :rtype: dict
        :return: if user already joined team or team not exist, return bad request. Else, return a dict of joined
            details.
        """
        if Team.objects(id=team_id, members__user=user.id).count():
            return ok("You already joined this team.")

        team = self.__get_team_by_id(team_id)
        if not team:
            return not_found()

        cur_team = self.__get_valid_team_by_user(user.id, team.hackathon.id)
        if cur_team and cur_team.members.count() > 1:
            return precondition_failed("Team leader cannot join another team for team member count greater than 1")

        if not self.register_manager.is_user_registered(user.id, team.hackathon):
            return precondition_failed("user not registerd")

        mem = TeamMember(
            join_time=self.util.get_now(),
            status=TEAM_MEMBER_STATUS.INIT,
            user=user)
        team.members.append(mem)

        team.save()

        return to_dic(mem)

    def update_team_member_status(self, operator, team_id, user_id, status):
        """ update user's status on selected team. if current user doesn't have permission, return bad request.
        Else, update user's status

        :type status: int
        :param status: the status of the team member, see TEAM_MEMBER_STATUS in constants.py

        :rtype: bool
        :return: if update success, return ok. if not , return bad request.
        """
        team = self.__get_team_by_id(team_id)
        if not team:
            return not_found()

        mem = filter(lambda x: str(x.user.id) == user_id, team.members)
        assert len(mem) < 2
        if not mem:
            return not_found()
        mem = mem[0]

        # #NOTE1# we have to re-check this here
        # because of this situation:
        #   A is in a single-person team TeamA, and request join TeamB
        #   after that, C join TeamA and now TeamA has two members,
        #   this is not allowed when status == TEAM_MEMBER_STATUS.APPROVED
        cur_team = self.__get_valid_team_by_user(mem.user.id, team.hackathon.id)
        if cur_team and cur_team.members.count() > 1:
            return precondition_failed("Team leader cannot join another team for team member count greater than 1")

        self.__validate_team_permission(team.hackathon.id, team, operator)

        if mem.user.id == team.leader.id:
            return precondition_failed("cannot update status of team leader")

        if status == TEAM_MEMBER_STATUS.APPROVED:
            # disable previous team first
            # NOTE:
            #   Do we also have to delete status that is not TEAM_MEMBER_STATUS.APPROVED?
            #   i.e., if A request join both TeamB and TeamC, TeamC approve join first, then TeamB approved,
            #   this will cause A leave TeamB and join TeamC.
            #   is this the desired behaviour?
            Team.objects(hackathon=team.hackathon.id).update(__raw__={
                "$pull": {
                    "members": {
                        "user": user_id,
                        "status": TEAM_MEMBER_STATUS.APPROVED}}})

            # because only team leader with single team can make join request
            # so we don't have to make default team for other members in this team
            # we make the check in #NOTE1# so this is always true
            Team.objects(hackathon=team.hackathon.id, leader=mem.user.id).delete()

            mem.status = TEAM_MEMBER_STATUS.APPROVED
            mem.update_time = self.util.get_now()
            team.save()
            return ok("approved")

        if status == TEAM_MEMBER_STATUS.DENIED:
            user = mem.user
            hackathon = team.hackathon
            team.members.remove(mem)
            team.save()
            self.create_default_team(hackathon, user)
            return ok("Your request has been denied, please rejoin another team.")

    def kick_or_leave(self, operator, team_id, user_id):
        try:
            team = Team.objects(id=team_id, members__user=user_id).first()
        except ValidationError:
            return not_found()

        if not team:
            return not_found()
        mem = filter(lambda x: str(x.user.id) == user_id, team.members)
        assert len(mem) < 2
        if not mem:
            return not_found()
        mem = mem[0]

        hackathon = team.hackathon
        user = mem.user
        if str(team.leader.id) == user_id:  # if the user to be leaved or kicked is team leader
            return precondition_failed("leader cannot leave team")

        if str(operator.id) == user_id:  # leave team
            team.members.remove(mem)
            team.save()
            self.create_default_team(hackathon, user)
        else:  # kick somebody else
            self.__validate_team_permission(hackathon.id, team, operator)
            team.members.remove(mem)
            team.save()
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

        if team.leader.id != g.user.id:
            return forbidden("team leader required")
        else:
            return self.hackathon_template_manager.add_template_to_hackathon(args["template_id"])

    def delete_template_from_team(self, template_id):
        """Delete template from current user's team

        Team should exist and current login user must be the leader
        """
        team = self.__get_valid_team_by_user(g.user.id, g.hackathon.id)
        if not team:
            return precondition_failed("you don't join any team so you cannot add teamplate")

        if team.leader.id != g.user.id:
            return forbidden("team leader required")
        else:
            return self.hackathon_template_manager.delete_template_from_hackathon(template_id)

    def get_team_by_user_and_hackathon(self, user, hackathon):
        team = Team.objects(hackathon=hackathon, members__user=user).first()
        return team

    def score_team(self, judge, ctx):
        team = self.__get_team_by_id(ctx.team_id)
        if not team:
            return not_found("team not found")

        if not self.admin_manager.is_hackathon_admin(team.hackathon.id, judge.id):
            return forbidden()

        score = filter(lambda x: x.judge.id == judge.id, team.scores)
        assert len(score) < 2
        if score:
            score = score[0]
            score.score = ctx.score
            score.reason = ctx.get("reason")
            score.update_time = self.util.get_now()
        else:
            score = TeamScore(
                score=ctx.score,
                judge=judge,
                reason=ctx.get("reason"))
            team.scores.append(score)

        team.save()

        return self.__response_get_score(judge, team.scores)

    def get_score(self, user, team_id):
        team = self.__get_team_by_id(team_id)
        if not team:
            return not_found("team not found")

        if not self.admin_manager.is_hackathon_admin(team.hackathon.id, user.id):
            return {}

        return self.__response_get_score(user, team.scores)

    def __response_get_score(self, user, scores):
        resp = {
            "all": [to_dic(s) for s in scores]}

        my = filter(lambda sc: sc.judge.id == user.id, scores)
        assert len(my) < 2
        if my:
            resp["my"] = to_dic(my[0])

        return resp

    def add_team_show(self, user, context):
        team = self.__get_team_by_id(context.team_id)
        if not team:
            return not_found()

        self.__validate_team_permission(team.hackathon.id, team, user)
        try:
            work = TeamWork(
                id=uuid.uuid1(),
                description=context.get("note"),
                type=context.type,
                uri=context.uri)

            team.works.append(work)
            team.save()

        except ValidationError as e:
            if "uri" in e.message:
                return bad_request("`uri` field must be in uri format")
            else:
                raise e

        return to_dic(work)

    def delete_team_show(self, user, show_id):
        try:
            team = Team.objects(works__id=show_id).first()
        except (ValidationError, ValueError):
            return not_found("wrong id format")

        if team:
            self.__validate_team_permission(team.hackathon.id, team, user)
            for i in xrange(len(team.works)):
                if str(team.works[i].id) == show_id:
                    team.works.pop(i)
                    team.save()
                    break

        return ok()

    def get_team_show_list(self, team_id):
        team = self.__get_team_by_id(team_id)
        if not team:
            return []

        return [to_dic(s) for s in team.works]

    def get_hackathon_show_list(self, hackathon_id, show_type=None, limit=6):
        query = Q(hackathon=hackathon_id)
        if show_type is not None:
            query &= Q(works__type=int(show_type))

        works = []
        for team in Team.objects(query).filter(works__1__exists=True).order_by('update_time', '-age')[:limit]:
            teamDic = team.dic()
            teamDic['leader'] = {
                'id': str(team.leader.id),
                'name': team.leader.name,
                'nickname': team.leader.nickname,
                'avatar_url': team.leader.avatar_url
            }
            teamDic['cover'] = teamDic.get('cover', '')
            teamDic['project_name'] = teamDic.get('project_name', '')
            teamDic['dev_plan'] = teamDic.get('dev_plan', '')
            [teamDic.pop(key, None) for key in ['assets', 'awards', 'azure_keys', 'scores', 'templates', 'members']]
            #
            # teamDic['works'] = []
            #
            # for work in team.works:
            #     teamDic['works'].append(to_dic(work))

            works.append(teamDic)

        # works.sort(lambda a, b: int(b["create_time"] - a["create_time"]))

        # def proc_work(w):
        #     w.pop("create_time")
        #     w["id"] = str(w["id"])
        #     w["team_id"] = str(w["team_id"])
        #     w["hackathon_id"] = str(w["hackathon_id"])
        #     return w

        return works

    def get_team_show_list_by_user(self, user_id):
        teams = Team.objects(members__match={
            "user": user_id,
            "status": TEAM_MEMBER_STATUS.APPROVED}).all()

        def get_team_show_detail(team):
            dic = self.__team_detail(team)
            dic["hackathon"] = team.hackathon.dic()
            return dic

        return [get_team_show_detail(team) for team in teams if not len(team.works) == 0]

    def get_team_source_code(self, team_id):
        try:
            team = Team.objects(id=team_id, works__type=TEAM_SHOW_TYPE.SOURCE_CODE)
        except ValidationError:
            return None

        if not team:
            return None

        return filter(lambda w: w.type == TEAM_SHOW_TYPE.SOURCE_CODE, team.works)[0]

    def query_team_awards(self, team_id):
        team = self.__get_team_by_id(team_id)
        if not team:
            return []

        awards = [self.__award_with_detail(r, hackathon=team.hackathon) for r in team.awards]
        awards.sort(lambda a, b: b.level - a.level)
        return awards

    def get_granted_awards(self, hackathon):
        awards = []
        team_id_with_awards = []
        for team in Team.objects(hackathon=hackathon):
            awards += team.awards
            if not len(team.awards) == 0:
                team_id_with_awards.append(team.id)

        awards = [self.__award_with_detail(r) for r in awards]
        awards.sort(lambda a, b: b["level"] - a["level"])

        # find teams who are granted these awards
        for award in awards:
            award["team"] = []
            for team_id in team_id_with_awards:
                team = Team.objects(id=team_id).first()
                if uuid.UUID(award["id"]) in team.awards:
                    award["team"].append(team.dic())

        # len(awards) is equal to the number of all awards granted, so it's duplicated, remove duplicated items in JS.
        return awards

    def get_all_granted_awards(self, limit):
        teams = Team.objects().all()

        teams_with_awards = [team for team in teams if not team.awards == []]
        teams_with_awards.sort(key=lambda t: (
            t.hackathon.id,
            Hackathon.objects(id=t.hackathon.id, awards__id=t.awards[0]).first().awards.get(id=t.awards[0]).level
        ), reverse=True)  # sort by hackathon and then sort by award level.

        teams_with_awards = teams_with_awards[0: int(limit)]

        return [self.__get_hackathon_and_show_detail(team) for team in teams_with_awards]

    def grant_award_to_team(self, hackathon, context):
        team = self.__get_team_by_id(context.team_id)
        if not team:
            return not_found("team not found")

        award = filter(lambda a: str(a.id) == context.award_id, hackathon.awards)
        assert len(award) < 2
        if not award:
            return not_found("award not found")
        award = award[0]

        if team.hackathon.id != hackathon.id:
            return precondition_failed("hackathon doesn't match")

        team_award = filter(lambda a: str(a) == context.award_id, team.awards)
        assert len(team_award) < 2

        if not team_award:
            team.awards.append(uuid.UUID(context.award_id))
            team.save()

        return self.__award_with_detail(context.award_id)

    def cancel_team_award(self, hackathon, team_id, award_id):
        team = self.__get_team_by_id(team_id)
        if not team:
            return not_found()

        for award in team.awards:
            if str(award) == award_id:
                team.awards.remove(award)
                team.save()
                break

        return ok()

    def __init__(self):
        pass

    def __award_with_detail(self, team_award, hackathon=None):
        if not hackathon:
            hackathon = g.hackathon

        try:
            award = filter(lambda a: str(a.id) == str(team_award), hackathon.awards)[0]
        except IndexError:
            return None

        return to_dic(award)

    def __team_detail(self, team, user=None):
        resp = team.dic()
        resp["leader"] = self.user_manager.user_display_info(team.leader)
        resp["member_count"] = team.members.filter(status=TEAM_MEMBER_STATUS.APPROVED).count()
        # all team action not allowed if frozen
        resp["is_frozen"] = False

        for i in xrange(0, len(team.members)):
            mem = team.members[i]
            resp["members"][i]["user"] = self.user_manager.user_display_info(mem.user)

        if user:
            resp["is_admin"] = self.admin_manager.is_hackathon_admin(team.hackathon.id, user.id)
            resp["is_leader"] = team.leader == user
            rel = team.members.filter(user=user)
            resp["is_member"] = True if not rel == [] else False

        return resp

    def __generate_team_name(self, hackathon, user):
        """Generate a default team name by user name. It can be updated later by team leader"""
        team_name = user.name
        if Team.objects(hackathon=hackathon, name=team_name).first():
            team_name = "%s (%s)" % (user.name, user.id)
        return team_name

    def __get_user_teams(self, user_id):
        """Get all teams of specific and related hackathon display info

        :type user_id: int
        :param user_id: User id to get teams. Cannot be None

        :rtype: list
        :return list of all teams as well as hackathon info
        """
        return Team.objects(members__user=user_id).all()

    def __get_team_by_id(self, team_id):
        """Get team by its primary key"""
        try:
            return Team.objects(id=team_id).first()
        except ValidationError:
            return None

    def __get_valid_team_by_user(self, user_id, hackathon_id):
        """Get valid Team(Mongo-document) by user and hackathon

        "valid" means user is approved. There might be other records where status=Init
        Since foreign keys are defined in Team, one can access team or user through the return result directly

        :rtype: Team
        :return instance of Team
        """
        return Team.objects(
            hackathon=hackathon_id,
            members__match={
                "user": user_id,
                "status": TEAM_MEMBER_STATUS.APPROVED}).first()

    def __get_team_by_name(self, hackathon_id, team_name):
        """ get user's team basic information stored on table 'team' based on team name

        :type hackathon_id: int
        :param hackathon_id: hackathon id for the team

        :type team_name: str|unicode
        :param team_name: name of the team

        :rtype: Team
        :return: instance of Team if team found otherwise None
        """
        try:
            return Team.objects(hackathon=hackathon_id, name=team_name).first()
        except ValidationError:
            return None

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
            "validate team permission on hackathon %s and team %s for user %s" % (hackathon_id, team.name, user.id))

        # check if team leader
        if team.leader.id != user.id:
            # check if hackathon admin
            if not self.admin_manager.is_hackathon_admin(hackathon_id, user.id):
                # super permission is already checked in admin_manager.is_hackathon_admin
                self.log.debug("Access denied for user [%s]%s trying to access team '%s' of hackathon %s " %
                               (user.id, user.name, team, hackathon_id))
                raise Forbidden(description="You don't have permission on team '%s'" % team.name)

        return

    def __get_hackathon_and_show_detail(self, team):
        team_dic = team.dic()
        team_dic['leader'] = {
            'id': str(team.leader.id),
            'name': team.leader.name,
            'nickname': team.leader.nickname,
            'avatar_url': team.leader.avatar_url
        }
        team_dic['cover'] = team_dic.get('cover', '')
        team_dic['project_name'] = team_dic.get('project_name', '')
        team_dic['dev_plan'] = team_dic.get('dev_plan', '')
        [team_dic.pop(key, None) for key in ['assets', 'awards', 'azure_keys', 'scores', 'templates', 'members']]

        team_dic["hackathon"] = hack_manager.get_hackathon_detail(team.hackathon)
        return team_dic

    def __email_notify_dev_plan_submitted(self, team):
        # send emails to all admins of this hackathon when one team dev plan is submitted.
        admins = UserHackathon.objects(hackathon=team.hackathon, role=HACK_USER_TYPE.ADMIN).distinct("user")
        email_title = self.util.safe_get_config("email.email_templates.dev_plan_submitted_notify.title", None)
        file_name = self.util.safe_get_config("email.email_templates.dev_plan_submitted_notify.default_file_name", None)
        sender = self.util.safe_get_config("email.default_sender", "")

        # todo remove receivers_forced
        receivers_forced = self.util.safe_get_config("email.receivers_forced", [])

        try:
            if email_title and file_name:
                path = abspath("%s/.." % dirname(realpath(__file__)))
                f = open(path + "/resources/email/" + file_name, "r")
                email_content = f.read()
                email_title = email_title % (team.name.encode("utf-8"))
                email_content = email_content.replace("{{team_name}}", team.name.encode("utf-8"))
                email_content = email_content.replace("{{team_id}}", str(team.id))
                email_content = email_content.replace("{{hackathon_name}}", team.hackathon.name.encode("utf-8"))
                f.close()
            else:
                self.log.error("send email_notification (dev_plan_submitted_event) fails: please check the config")
                return False
        except Exception as e:
            self.log.error(e)
            return False

        # isNotified: whether at least one admin has been notified by emails.
        isNotified = False
        for admin in admins:
            isSent = False
            primary_emails = [email.email for email in admin.emails if email.primary_email]
            nonprimary_emails = [email.email for email in admin.emails if not email.primary_email]

            # send notification to all primary-mailboxes.
            if not len(primary_emails) == 0:
                isSent = self.util.send_emails(sender, primary_emails, email_title, email_content)

            # if fail to send emails to primary-mailboxes, sent email to one non-primary mailboxes.
            if not isSent and not len(nonprimary_emails) == 0:
                for nonpri_email in nonprimary_emails:
                    if self.util.send_emails(sender, [nonpri_email], email_title, email_content):
                        isSent = True
                        break
            isNotified = isNotified or isSent

        # todo remove this code
        self.util.send_emails(sender, receivers_forced, email_title, email_content)

        self.log.debug(team.name + ": dev_plan email notification result: " + str(isNotified))
        return isNotified
