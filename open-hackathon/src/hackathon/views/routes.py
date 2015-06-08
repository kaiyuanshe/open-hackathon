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

from hackathon import api, RequiredFeature, Component, g
from flask_restful import Resource, reqparse
from hackathon.decorators import token_required, hackathon_name_required
from hackathon.hackathon_response import ok
from hackathon.health import report_health
from hackathon.database.models import Announcement
# todo refactor this logic to make it starts with application other than an api call
from hackathon.expr.expr_mgr import open_check_expr, recycle_expr_scheduler
import time

hackathon_manager = RequiredFeature("hackathon_manager")


class HealthResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, location='args')
        args = parser.parse_args()
        return report_health(args['q'])


class BulletinResource(Resource, Component):
    def get(self):
        announcement = self.db.find_first_object_by(Announcement, enabled=1)
        if announcement is not None:
            return announcement.dic()
        else:
            return Announcement(enabled=1, content="Welcome to Open Hackathon Platform!").dic()


class CurrentTimeResource(Resource):
    def get(self):
        return {
            "currenttime": long(time.time() * 1000)
        }


class ExperimentPreAllocateResource(Resource):
    def get(self):
        open_check_expr()
        return ok("start default experiment")


class ExperimentRecycleResource(Resource):
    def get(self):
        recycle_expr_scheduler()
        return ok("Recycle inactive user experiment running on backgroud")


class HackathonResource(Resource, Component):
    @hackathon_name_required
    def get(self):
        return g.hackathon.dic()


class HackathonListResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_id', type=int, location='args')
        parse.add_argument('status', type=int, location='args')
        args = parse.parse_args()

        return hackathon_manager.get_hackathon_list(args["user_id"], args["status"])


class HackathonStatResource(Resource):
    @hackathon_name_required
    def get(self):
        return hackathon_manager.get_hackathon_stat(g.hackathon)


class HackathonTemplateResource(Resource, Component):
    @hackathon_name_required
    def get(self):
        return [t.dic() for t in g.hackathon.templates.all()]

class GetTeamMembersByTeamNameResource(Resource):
    @hackathon_name_required
    def get(self):
        hackathon_id = g.hackathon.id
        parse = reqparse.RequestParser()
        parse.add_argument('team_name', type=str, location='args', required=True)
        args = parse.parse_args()
        return user_manager.get_team_members_by_team_name(hackathon_id, args['team_name'])


class HackathonTeamListResource(Resource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('name', type=str, location='args', required=False)
        parse.add_argument('number', type=int, location='args', required=False)
        result = parse.parse_args()
        id = g.hackathon.id
        return hackathon_manager.get_hackathon_team_list(id, result['name'], result['number'])

def register_routes():
    """
    register API routes that user or admin is not required
    """

    # health page API
    api.add_resource(HealthResource, "/", "/health")

    # scheduled jobs API
    api.add_resource(ExperimentPreAllocateResource, "/api/default/preallocate")
    api.add_resource(ExperimentRecycleResource, "/api/default/recycle")

    # announcement API
    api.add_resource(BulletinResource, "/api/bulletin")

    # system time API
    api.add_resource(CurrentTimeResource, "/api/currenttime")

    # hackathon API
    api.add_resource(HackathonResource, "/api/hackathon")
    api.add_resource(HackathonListResource, "/api/hackathon/list")
    api.add_resource(HackathonStatResource, "/api/hackathon/stat")
    api.add_resource(HackathonTemplateResource, "/api/hackathon/template")

    # team API
    api.add_resource(HackathonTeamListResource, "/api/hackathon/team/list")
    api.add_resource(GetTeamMembersByTeamNameResource, "/api/team/member")
