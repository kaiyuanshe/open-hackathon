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
from hackathon.database.models import Template
from hackathon.database import db_adapter
from hackathon.hack import hack_manager
from flask import g
from hackathon.hackathon_response import *
from datetime import datetime
from hackathon.enum import TEMPLATE_STATUS


class TemplateManager(object):
    def __init__(self, db_adapter):
        self.db = db_adapter


    def get_template_list(self, hackathon_name):
        hackathon = hack_manager.get_hackathon_by_name(hackathon_name)
        if hackathon is None:
            return {'errercode': 404, 'message': 'hackathon not found'}
        hack_id = hackathon.id
        templates = self.db.find_all_objects_by(Template, hackathon_id=hack_id)
        return map(lambda u: u.dic(), templates)


    def get_template_by_id(self, id):
        return self.db.find_first_object(Template, Template.id == id)


    def create_template(self, args):
        if "name" not in args:
            return bad_request("template perporities lost name")
        template = self.db.find_first_object(Template, Template.name == args['name'])

        if template is  not None:
            return bad_request("template aready exist")

        try:
            log.debug("create template: %r" % args)
            args['creator_id'] = g.user.id
            args['update_time'] = datetime.utcnow()
            args['hackathon_id'] = g.hackathon.id
            args['status'] = TEMPLATE_STATUS.ONLINE
            return self.db.add_object_kwargs(Template, **args)
        except Exception as ex:
            log.error(ex)
            return internal_server_error("create or update failed because of raising Exception")

    def update_template(self, args):
        if "name" not in args:
            return bad_request("template perporities lost name")
        template = self.db.find_first_object(Template, Template.name == args['name'])

        if template is None:
            return bad_request("template doesn't exist")
        try:

            log.debug("update template: %r" % args)
            args['update_time'] = datetime.utcnow()
            update_items = dict(dict(args).viewitems() - template.dic().viewitems())
            log.debug("update a exist hackathon :" + str(args))
            self.db.update_object(template, **update_items)
            return ok("update template success")
        except Exception as ex:
            log.error(ex)
            return internal_server_error("create or update failed because of raising Exception")

    def delete_template(self, id):
        log.debug("delete or disable a exist template")
        try:
            template = self.get_template_by_id(id)
            args = {}
            args['status'] = TEMPLATE_STATUS.OFFLINE
            args['update_time'] = datetime.utcnow()
            self.db.update_object(template, args)
            return ok("delete or disable template success")
        except Exception as ex:
            log.error(ex)
            return internal_server_error("disable or delete failed")


template_manager = TemplateManager(db_adapter)