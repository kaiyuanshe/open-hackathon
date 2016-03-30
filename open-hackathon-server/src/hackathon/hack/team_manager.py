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
from mongoengine import Q

from hackathon import Component, RequiredFeature
from hackathon.hmongo.models import Team, TeamMember, TeamScore, TeamWork, Hackathon, to_dic
from hackathon.hackathon_response import not_found, bad_request, precondition_failed, ok, forbidden
from hackathon.constants import TEAM_MEMBER_STATUS, TEAM_SHOW_TYPE

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
        team = Team.objects(id=team_id).first()

        if not team:
            return None

        def sub(t):
            m = t.dic()
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
        teams = Team.objects(hackathon=hackathon_id)
        if name is not None:
            teams = filter(lambda t: name in t.name, teams)
        if number is not None:
            teams = teams[0: number]

        # check whether it's anonymous user or not
        user = None
        if self.user_manager.validate_login():
            user = g.user

        return map(lambda x: self.__team_detail(x, user), teams)

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

        team.name = kwargs.get("name", team.name),
        team.description = kwargs.get("description", team.description),
        team.logo = kwargs.get("logo", team.logo),
        team.update_time = self.util.get_now()
        team.save()

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
                    if u != user:
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
        :param user: the user to join a team

        :rtype: dict
        :return: if user already joined team or team not exist, return bad request. Else, return a dict of joined
            details.
        """
        if Team.objects(id=team_id, members__user=user.id).count():
            return ok("You already joined this team.")

        team = self.__get_team_by_id(team_id)
        if not team:
            return not_found()

        cur_team = self.__get_valid_team_by_user(user.id, team.hackathon_id)
        if cur_team and cur_team.team.user_team_rels.count() > 1:
            return precondition_failed("Team leader cannot join another team for team member count greater than 1")

        if not self.register_manager.is_user_registered(user.id, team.hackathon):
            return precondition_failed("user not registerd")

        mem = TeamMember(
            join_time=self.util.get_now(),
            status=TEAM_MEMBER_STATUS.INIT,
            user_id=user.id)
        team.members.push(mem)

        team.save()

        return to_dic(mem)

    def update_team_member_status(self, operator, team_id, status):
        """ update user's status on selected team. if current user doesn't have permission, return bad request.
        Else, update user's status

        :type status: int
        :param status: the status of the team member, see TEAM_MEMBER_STATUS in constants.py

        :rtype: bool
        :return: if update success, return ok. if not , return bad request.
        """
        team = Team.objects(id=team_id)
        mem = filter(lambda x: x.user.id == operator.id, team.members)
        assert len(mem) < 2
        if not mem:
            return not_found()
        mem = mem[0]

        self.__validate_team_permission(team.hackathon.id, team, operator)

        if operator.user.id == team.leader.id:
            return precondition_failed("cannot update status of team leader")

        if status == TEAM_MEMBER_STATUS.APPROVED:
            # disable previous team first
            Team.objects(hackathon=team.hackathon.id).update(pull__members__user={
                "user": operator.id,
                "status": TEAM_MEMBER_STATUS.APPROVED})

            Team.objects(hackathon=team.hackathon.id, leader=operator.id).delete()

            mem.status = TEAM_MEMBER_STATUS.APPROVED
            mem.update_time = self.util.get_now()
            team.save()
            return ok("approved")

        if status == TEAM_MEMBER_STATUS.DENIED:
            user = mem.user
            hackathon = mem.hackathon
            team.members.remove(mem)
            self.create_default_team(hackathon, user)
            return ok("Your request has been denied, please rejoin another team.")

    def kick_or_leave(self, operator, team_id, user_id):
        team = Team.objects(id=team_id, members__user=user_id)
        if not team:
            return not_found()
        mem = filter(lambda x: x.user.id == user_id, team.members)[0]

        hackathon = team.hackathon
        user = mem.user
        if team.leader.id == user_id:  # if the user to be leaved or kicked is team leader
            return precondition_failed("leader cannot leave team")

        if operator.id == user_id:  # leave team
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
            return self.hackathon_template_manager.add_template_to_hackathon(args["template_id"], team.id)

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
            return self.hackathon_template_manager.delete_template_from_hackathon(template_id, team.id)

    def get_team_by_user_and_hackathon(self, user, hackathon):
        team = Team.objects(hackathon=hackathon, members__user=user).first()
        return team

    def score_team(self, judge, ctx):
        team = self.__get_team_by_id(ctx.team_id)
        if not team:
            return not_found("team not found")

        if not self.admin_manager.is_hackathon_admin(team.hackathon_id, judge.id):
            return forbidden()

        score = filter(lambda x: x.judge.id == judge.id, team.scores)
        if score:
            score = score[0]
            score.score = ctx.score
            score.reason = ctx.get("reason")
            score.update_time = self.util.get_now()
            team.save()
        else:
            score = TeamScore(
                score=ctx.score,
                judge=judge,
                reason=ctx.get("reason"))
            team.scores.append(score)
            team.save()

        return self.get_score(judge, team.id)

    def get_score(self, user, team_id):
        team = self.__get_team_by_id(team_id)
        if not team:
            return not_found("team not found")

        if not self.admin_manager.is_hackathon_admin(team.hackathon_id, user.id):
            return {}

        resp = {
            "all": [s.dic() for s in team.scores]}

        my = filter(lambda sc: sc.judge.id == user.id, team.scores)
        if len(my):
            resp["my"] = my[0].dic()

        return resp

    def add_team_show(self, user, context):
        team = self.__get_team_by_id(context.team_id)
        if not team:
            return not_found()

        self.__validate_team_permission(team.hackathon_id, team, user)
        work = TeamWork(
            note=context.get("note"),
            type=context.type,
            uri=context.uri,
            team_id=context.team_id,
            hackathon_id=team.hackathon_id)

        self.db.add_object(work)
        return to_dic(work)

    def delete_team_show(self, user, show_id):
        team = Team.objects(works__id=show_id).first()
        if team:
            self.__validate_team_permission(team.hackathon_id, team, user)
            for i in xrange(len(team.works)):
                if str(team.works[i].id) == show_id:
                    team.works.pop(i)
                    break
            team.save()

        return ok()

    def get_team_show_list(self, team_id):
        team = self.__get_team_by_id(team_id)
        if not team:
            return []

        return [to_dic(s) for s in team.works]

    def get_hackathon_show_list(self, hackathon_id, show_type=None, limit=10):
        query = Q(hackathon=hackathon_id)
        if show_type:
            query &= Q(works__type=show_type)
        # show_list = TeamShow.query.filter(criterion).order_by(TeamShow.create_time.desc()).limit(limit)
        works = []
        for team in Team.objects(query):
            works += team.works

        works.sort(lambda a, b: b.create_time - a.create_time)
        works = works[:limit]

        def fill_work(w):
            return {
                "name": w.team.name,
                "description": w.team.description,
                "logo": w.team.logo,
                "uri": "",  # TODO: what is uri?
                "id": w.id,
                "note": w.note,
                "team_id": w.team.id,
                "hackathon_id": w.hackathon.id}

        return [fill_work(w) for w in works]

    def get_team_source_code(self, team_id):
        team = Team.objects(id=team_id, works__type=TEAM_SHOW_TYPE.SOURCE_CODE)
        if not team:
            return None

        return filter(lambda w: w.type == TEAM_SHOW_TYPE.SOURCE_CODE, team.works)[0]

    def query_team_awards(self, team_id):
        team = self.__get_team_by_id(team_id)
        if not team:
            return []

        return [self.__award_with_detail(r) for r in sorted(team.awards, lambda a, b: b.level - a.level)]

    def get_granted_awards(self, hackathon):
        # awards = self.db.find_all_objects_order_by(TeamAward,
        #                                            None,
        #                                            TeamAward.level.desc(), TeamAward.create_time.asc(),
        #                                            hackathon_id=hackathon.id)
        # return [self.__award_with_detail(r) for r in awards]
        # TODO
        pass

    def get_all_granted_awards(self, limit):

        teams = Team.objects.all()
        teams_with_awards = [team for team in teams if not team.awards == []]
        teams_with_awards.sort(key=lambda t:(
            t.hackathon.id,
            Hackathon.objects(id=t.hackathon.id, awards__id=t.awards[0]).first().awards[0].level
            ), reverse=True) # sort by hackathon and then sort by award level.
        teams_with_awards = teams_with_awards[0: int(limit)]

        return [self.__get_hackathon_and_show_detail(team) for team in teams_with_awards]

    def grant_award_to_team(self, hackathon, context):
        # team = self.__get_team_by_id(context.team_id)
        # if not team:
        #     return not_found("team not found")
        #
        # award = self.db.find_first_object_by(Award, id=context.award_id)
        # if not award:
        #     return not_found("award not found")
        #
        # if team.hackathon_id != hackathon.id or award.hackathon_id != hackathon.id:
        #     return precondition_failed("hackathon doesn't match")
        #
        # exist = self.db.find_first_object_by(TeamAward, team_id=context.team_id, award_id=context.award_id)
        # if not exist:
        #     exist = TeamAward(team_id=context.team_id,
        #                       hackathon_id=hackathon.id,
        #                       award_id=context.award_id,
        #                       reason=context.get("reason"),
        #                       level=award.level)
        #     self.db.add_object(exist)
        # else:
        #     exist.reason = context.get("reason", exist.reason)
        #     self.db.commit()
        #
        # return self.__award_with_detail(exist)
        # TODO
        pass

    def cancel_team_award(self, hackathon, team_award_id):
        # self.db.delete_all_objects_by(TeamAward, hackathon_id=hackathon.id, id=team_award_id)
        # return ok()
        # TODO
        pass

    def __init__(self):
        pass

    def __award_with_detail(self, team_award_rel):
        dic = team_award_rel.dic()
        dic["award"] = team_award_rel.award.dic()
        return dic

    def __team_detail(self, team, user=None):
        resp = team.dic()
        resp["leader"] = self.user_manager.user_display_info(team.leader)
        resp["member_count"] = team.members.filter(status=TEAM_MEMBER_STATUS.APPROVED).count()
        # all team action not allowed if frozen
        resp["is_frozen"] = team.hackathon.judge_start_time < self.util.get_now()

        if user:
            resp["is_admin"] = self.admin_manager.is_hackathon_admin(team.hackathon.id, user.id)
            resp["is_leader"] = team.leader == user
            rel = Team.objects().filter(members__user=user).count()
            resp["is_member"] = rel > 0

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
        return Team.objects(id=team_id).first()

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
        return Team.objects(hackathon=hackathon_id, name=team_name).first()

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
                # super permission is already checked in admin_manager.is_hackathon_admin
                self.log.debug("Access denied for user [%s]%s trying to access team '%s' of hackathon %d " %
                               (user.id, user.name, team, hackathon_id))
                raise Forbidden(description="You don't have permission on team '%s'" % team)

        return

    def __get_hackathon_and_show_detail(self, team):
        team_dic = team.dic()
        team_dic["hackathon"] = hack_manager.get_hackathon_detail(team.hackathon)
        return team_dic