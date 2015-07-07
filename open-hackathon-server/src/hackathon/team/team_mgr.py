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
from hackathon.database.models import UserTeamRel, User, Team, UserHackathonRel
from datetime import timedelta
from hackathon.constants import HTTP_HEADER
from flask import request, g
from hackathon import Component, RequiredFeature


class TeamManager(Component):

    def get_team_by_id(self, team_id):
        return self.db.find_first_project_by(Team, id=team_id)

    def get_team_by_name(self, team_name):
        return self.db.find_first_project_by(Team, name=team_name)

    def get_team_by_user_and_hackathon(self, user, hackathon):
        utrs = self.db.find_all_projects_by(UserTeamRel, user_id=user.id)
        team_ids = map(lambda x: x.team_id, utrs)
        team = self.db.find_first_project(Team, Team.id.in_(team_ids), Team.hackathon_id==hackathon.id)
        return team