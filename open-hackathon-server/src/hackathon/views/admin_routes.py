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

from flask_restful import Resource, reqparse
from flask import g, request

from hackathon import api, RequiredFeature
from hackathon.decorators import hackathon_name_required, admin_privilege_required
from hackathon.hackathon_response import not_found, bad_request

__all__ = ["register_admin_routes"]

hackathon_manager = RequiredFeature("hackathon_manager")
register_manager = RequiredFeature("register_manager")
template_manager = RequiredFeature("template_manager")
admin_manager = RequiredFeature("admin_manager")
expr_manager = RequiredFeature("expr_manager")


class AdminRegisterListResource(Resource):
    @admin_privilege_required
    def get(self):
        return register_manager.get_hackathon_registration()


class AdminRegisterResource(Resource):
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)  # register_id
        args = parse.parse_args()
        rel = register_manager.get_registration_by_id(args["id"])
        return rel.dic() if rel is not None else not_found("not found")

    @admin_privilege_required
    def post(self):
        args = request.get_json()
        return register_manager.create_registration(g.hackathon, args)

    @admin_privilege_required
    def put(self):
        args = request.get_json()
        return register_manager.update_registration(args)

    @admin_privilege_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return register_manager.delete_registration(args)


class AdminHackathonTemplateListResource(Resource):
    @hackathon_name_required
    def get(self):
        templates = template_manager.get_templates_by_hackathon_id(g.hackathon.id)
        return map(lambda x: x.dic(), templates)


class AdminHackathonTemplateResource(Resource):
    # create a h-t-r for hacakthon
    @admin_privilege_required
    def post(self):
        args = request.get_json()
        if "template_id" not in args:
            return bad_request("template id invalid")
        return template_manager.add_template_to_hackathon(args['template_id'])

    # delete a h-t-r for hacakthon
    @admin_privilege_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('template_id', type=int, location='args', required=True)
        args = parse.parse_args()
        return template_manager.delete_template_from_hackathon(args['template_id'])


class ExperimentListResource(Resource):
    @admin_privilege_required
    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('user_name', type=str, location='args')
        parse.add_argument('status', type=int, location='args')
        args = parse.parse_args()
        return expr_manager.get_expr_list_by_hackathon_id(g.hackathon.id,
                                                          user_name=args['user_name'],
                                                          status=args['status'])


class AdminExperimentResource(Resource):
    @admin_privilege_required
    def post(self):
        args = request.get_json()
        if 'name' not in args:
            return bad_request('template name name invalid')
        template_name = args['name']
        user_id = g.user.id
        hackathon_name = g.hackathon.name
        return expr_manager.start_expr(hackathon_name, template_name, user_id)

    @admin_privilege_required
    def put(self):
        args = request.get_json()
        if 'experiment_id' not in args:
            return bad_request('experiment id invalid')
        return expr_manager.stop_expr(args['experiment_id'])


class HackathonFileResource(Resource):
    @admin_privilege_required
    def post(self):
        return hackathon_manager.upload_files()

    def delete(self):
        # TODO call storage api to delete file
        return True


class HackathonAdminListResource(Resource):
    @hackathon_name_required
    def get(self):
        return admin_manager.get_admins_by_hackathon(g.hackathon)


class HackathonAdminResource(Resource):
    @admin_privilege_required
    def post(self):
        args = request.get_json()
        return admin_manager.add_admin(args)

    @admin_privilege_required
    def put(self):
        args = request.get_json()
        return admin_manager.update_admin(args)

    @admin_privilege_required
    def delete(self):
        parse = reqparse.RequestParser()
        parse.add_argument('id', type=int, location='args', required=True)
        args = parse.parse_args()
        return admin_manager.delete_admin(args['id'])


def register_admin_routes():
    """
    register API routes for admin site
    """
    # registration APIs
    api.add_resource(AdminRegisterListResource, "/api/admin/registration/list")
    api.add_resource(AdminRegisterResource, "/api/admin/registration")

    # template APIs
    api.add_resource(AdminHackathonTemplateResource, "/api/admin/hackathon/template")
    api.add_resource(AdminHackathonTemplateListResource, "/api/admin/hackathon/template/list")

    # experiment APIs
    api.add_resource(AdminExperimentResource, "/api/admin/experiment")
    api.add_resource(ExperimentListResource, "/api/admin/experiment/list")

    # file upload
    api.add_resource(HackathonFileResource, "/api/admin/file")

    # hackathon administrators
    api.add_resource(HackathonAdminListResource, "/api/admin/hackathon/administrator/list")
    api.add_resource(HackathonAdminResource, "/api/admin/hackathon/administrator")
