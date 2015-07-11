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

    def team_approve(self,hid,tname,uid):
        candidate=self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, team_name=tname, user_id=uid)
        candidate.status = 1
        self.db.update_object()

    def team_refuse(self,hid,tname,uid):
        candidate=self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, team_name=tname, user_id=uid)
        candidate.status = 2
        self.db.update_object()

    def team_kick(self,hid,tname,uid):
        candidate=self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, team_name=tname, user_id=uid)
        candidate.status = 0
        self.db.update_object()

    def team_leave(self,hid,tname,uid):
        candidate=self.db.find_first_object_by(UserTeamRel, hackathon_id=hid, team_name=tname, user_id=uid)
        if candidate is not None:
            self.db.update_object()

    def promo_leader(self,hid,tname,new_uid,old_uid):
        leader = self.db.find_first_object_by(Team, hackathon_id=hid, team_)

    def team_dismiss(self,hid,tname,uid):
