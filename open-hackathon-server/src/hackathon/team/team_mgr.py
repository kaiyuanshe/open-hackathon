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
from hackathon import Component
from hackathon.database.models import Team, UserTeamRel


class TeamManager(Component):
    def check_leader(self, hid, tname, uid):
        leader = self.db.find_first_object_by(Team, team_name=tname, leader_id=uid)
        if leader is None:
            return log.debug("You are not team leader yet, can't use this function")

    def team_approve(self, hid, uid):
        candidate = self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=uid)
        candidate.status = 1
        self.db.update_object()

    def team_refuse(self, hid, uid):
        candidate = self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=uid)
        candidate.status = 2
        self.db.update_object()

    def team_kick(self, hid, uid):
        candidate = self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=uid)
        candidate.status = 0
        self.db.update_object(candidate)

    def team_leave(self, hid, uid):
        candidate = self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, user_id=uid)
        if candidate is not None:
            self.db.delete_object(candidate)

    def promo_leader(self, hid, tname, new_uid, old_uid):
        leader = self.db.find_first_object_by(Team, hackathon_id=hid, team_name=tname, leader_id=old_uid)
        leader.leader_id = new_uid
        self.db.update_object(leader)

    def team_dismiss(self, hid, tname, uid):
        team = self.db.find_first_object_by(Team, hackathon_id=hid, team_name=tname)
        member = self.db.find_all_objects_order_by(UserTeamRel, Team_id=team.id)
        lambda x: self.db.delete_object(x), member
        self.db.delete_object(team)
