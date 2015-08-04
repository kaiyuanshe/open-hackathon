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

from hackathon import api, RequiredFeature, Component
from flask import g, request
from flask_restful import Resource, reqparse
from hackathon.decorators import hackathon_name_required, token_required
from hackathon.health import report_health
from hackathon.database.models import Announcement
import time
from hackathon.hackathon_response import not_found

hackathon_manager = RequiredFeature("hackathon_manager")
user_manager = RequiredFeature("user_manager")
register_manager = RequiredFeature("register_manager")
template_manager = RequiredFeature("template_manager")
team_manager = RequiredFeature("team_manager")
import inspect

class HealthResource(Resource):
    @hackathon_name_required
    def get(self):
        print(inspect.stack()[0][0].f_code.co_name)
        print(inspect.stack()[0][3])
        print(inspect.currentframe().f_code.co_name)
        print(sys._getframe().f_code.co_name)
        print self.__class__.__name__
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


class HackathonUserTemplateResource(Resource, Component):
    @token_required
    @hackathon_name_required
    def get(self):
        return template_manager.get_user_templates(g.user, g.hackathon)


class HackathonRegisterResource(Resource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('num', type=int, location='args', default=5)
        args = parse.parse_args()
        return register_manager.get_hackathon_registration(args['num'])


class HackathonTeamListResource(Resource):
    @hackathon_name_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('name', type=str, location='args', required=False)
        parse.add_argument('number', type=int, location='args', required=False)
        result = parse.parse_args()
        id = g.hackathon.id
        return team_manager.get_hackathon_team_list(id, result['name'], result['number'])


class TemplateResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=False)
        args = parse.parse_args()
        template = template_manager.get_template_by_id(args['id'])
        return template.dic() if template is not None else not_found("not found")

    # create template
    @token_required
    def post(self):
        args = request.get_json()
        return template_manager.create_template(args)

    # modify template
    @token_required
    def put(self):
        args = request.get_json()
        return template_manager.update_template(args)

    # delete template
    @token_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return template_manager.delete_template(args['id'])


class TemplateCreateByFileResource(Resource):
    # create template by file
    @token_required
    def post(self):
        return template_manager.create_template_by_file()


class TemplateListResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('status', type=int, location='args',required=False)
        parse.add_argument('name', type=str, location='args',required=False)
        parse.add_argument('description', type=str, location='args', required=False)
        args = parse.parse_args()
        templates = template_manager.get_template_list(status=args['status'],
                                                       name=args['name'],
                                                       description=args['description'])
        return map(lambda x: x.dic(), templates)


class HackathonTemplateListResource(Resource):
    @hackathon_name_required
    def get(self):
        templates = template_manager.get_templates_by_hackathon_id(g.hackathon.id)
        return map(lambda x: x.dic(), templates)


def register_routes():
    """
    register API routes that user or admin is not required
    """

    # health page API
    api.add_resource(HealthResource, "/", "/health")

    # announcement API
    api.add_resource(BulletinResource, "/api/bulletin")

    # system time API
    api.add_resource(CurrentTimeResource, "/api/currenttime")

    # hackathon API
    api.add_resource(HackathonResource, "/api/hackathon")
    api.add_resource(HackathonListResource, "/api/hackathon/list")
    api.add_resource(HackathonStatResource, "/api/hackathon/stat")
    api.add_resource(HackathonUserTemplateResource, "/api/hackathon/template")

    # team API
    api.add_resource(HackathonTeamListResource, "/api/hackathon/team/list")

    # hackathon register api
    api.add_resource(HackathonRegisterResource, "/api/hackathon/registration/list")

    # template API
    api.add_resource(TemplateResource, "/api/template")
    api.add_resource(TemplateCreateByFileResource, "/api/template/file")
    api.add_resource(TemplateListResource, "/api/template/list")
    api.add_resource(HackathonTemplateListResource, "/api/admin/hackathon/template/list")
