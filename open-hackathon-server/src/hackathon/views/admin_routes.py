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

from hackathon import api, RequiredFeature, Component
from hackathon.decorators import token_required, hackathon_name_required, admin_privilege_required
from hackathon.hackathon_response import not_found, bad_request, internal_server_error

__all__ = ["register_admin_routes"]

hackathon_manager = RequiredFeature("hackathon_manager")
register_manager = RequiredFeature("register_manager")
template_manager = RequiredFeature("template_manager")
azure_cert_management = RequiredFeature("azure_cert_management")
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


class AdminAzureResource(Resource, Component):
    @hackathon_name_required
    def get(self):
        certificates = azure_cert_management.get_certificates(g.hackathon.name)
        if certificates is None:
            return not_found("no certificates")
        return certificates, 200

    @hackathon_name_required
    def post(self):
        args = request.get_json()
        if 'subscription_id' not in args or 'management_host' not in args:
            return bad_request("subscription_id or management_host invalid")
        subscription_id = args['subscription_id']
        management_host = args['management_host']
        try:
            azure_cert_url = azure_cert_management.create_certificate(subscription_id, management_host,
                                                                      g.hackathon.name)
            return {'azure_cert_url': azure_cert_url}, 200
        except Exception as err:
            self.log.error(err)
            return internal_server_error('fail to create certificate due to [%s]' % err)

    @hackathon_name_required
    def delete(self):
        args = request.get_json()
        if 'certificate_id' not in args:
            return bad_request("certificate_id invalid")
        certificate_id = args['certificate_id']
        if azure_cert_management.delete_certificate(certificate_id, g.hackathon.name):
            return {'message': 'certificate deleted'}, 200
        else:
            return internal_server_error("fail to delete certificate")


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

    # hackathon api



    # registration APIs
    api.add_resource(AdminRegisterListResource, "/api/admin/registration/list")
    api.add_resource(AdminRegisterResource, "/api/admin/registration")

    # template APIs
    api.add_resource(AdminHackathonTemplateResource, "/api/admin/hackathon/template")
    api.add_resource(AdminHackathonTemplateListResource, "/api/admin/hackathon/template/list")

    # experiment APIs
    api.add_resource(AdminExperimentResource, "/api/admin/experiment")
    api.add_resource(ExperimentListResource, "/api/admin/experiment/list")

    # azure resources
    api.add_resource(AdminAzureResource, '/api/admin/azure')

    # file upload
    api.add_resource(HackathonFileResource, "/api/admin/file")

    # hackathon administrators
    api.add_resource(HackathonAdminListResource, "/api/admin/hackathon/administrator/list")
    api.add_resource(HackathonAdminResource, "/api/admin/hackathon/administrator")
