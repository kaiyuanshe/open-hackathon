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
from werkzeug.exceptions import BadRequest, InternalServerError, Forbidden

sys.path.append("..")
from os.path import isfile
import json
import requests

from sqlalchemy import and_
from flask import g, request

from hackathon import Component, RequiredFeature, Context
from hackathon.database import Template, Experiment, HackathonTemplateRel
from hackathon.hackathon_response import not_found, ok, internal_server_error, forbidden
from hackathon.constants import FILE_TYPE, TEMPLATE_STATUS
from template_constants import TEMPLATE
from template_content import TemplateContent

__all__ = ["TemplateLibrary"]


class TemplateLibrary(Component):
    """Component to manage templates"""

    storage = RequiredFeature("storage")
    user_manager = RequiredFeature("user_manager")

    def get_template_info_by_id(self, template_id):
        """Query template basic info from DB by its id

        :type template_id: int
        :param template_id: unique id of Template
        """
        template = self.db.get_object(Template, template_id)
        if template:
            return template.dic()
        return not_found("template cannot be found by id %s" % template_id)

    def get_template_info_by_name(self, template_name):
        """Query template basic info from DB by its id

        :type template_name: str|unicode
        :param template_name: unique name of Template
        """
        return self.db.find_first_object_by(Template, name=template_name)

    def search_template(self, args):
        """Search template by status, name or description"""
        criterion = self.__generate_search_criterion(args)
        templates = self.db.find_all_objects(Template, criterion)
        return [t.dic() for t in templates]

    def load_template(self, template):
        """load template into memory either from a local cache path or an remote uri
        load template from local file > from from azure
        :param template:
        :return:
        """

        def internal_load_template():
            local_path = template.local_path
            if local_path is not None and isfile(local_path):
                with open(local_path) as template_file:
                    return TemplateContent.from_dict(json.load(template_file))
            else:
                try:
                    req = requests.get(template.url)
                    return TemplateContent.from_dict(json.loads(req.content))
                except Exception as e:
                    self.log.warn("Fail to load template from remote file %s" % template.url)
                    self.log.error(e)
                    return None

        cache_key = self.__get_template_cache_key(template.id)
        return self.cache.get_cache(key=cache_key, createfunc=internal_load_template)

    def create_template(self, args):
        """ Create template """
        template_content = self.__load_template_content(args)
        return self.__create_or_update_template(template_content)

    def create_template_by_file(self):
        """create a template from uploaded file

        The whole logic contains 4 main steps:
        1 : get template dic from PostRequest
        2 : args validate
        3 : parse args and save to storage
        4 : save to database

        :return:
        """
        template_dic = self.__get_template_from_request()
        template_content = self.__load_template_content(template_dic)
        return self.__create_or_update_template(template_content)

    def update_template(self, args):
        """update a exist template

        The whole logic contains 3 main steps:
        1 : args validate for update operation
        2 : parse args and save to storage
        3 : save to database

        :type args: dict
        :param args: description of the template that you want to create

        :return:
        """
        template_content = self.__load_template_content(args)
        template = self.__get_template_by_name(template_content.name)
        if template is not None:
            # user can only modify the template which created by himself except super admin
            if g.user.id != template.creator_id and not self.user_manager.is_super_admin(g.user):
                raise Forbidden()

        return self.__create_or_update_template(template_content)

    def delete_template(self, template_id):
        self.log.debug("delete template [%d]" % template_id)
        try:
            template = self.db.get_object(Template, template_id)
            if template is None:
                return ok("already removed")
            # user can only delete the template which created by himself except super admin
            if g.user.id != template.creator_id and not self.user_manager.is_super_admin(g.user):
                return forbidden()
            if len(self.db.find_all_objects_by(Experiment, template_id=template_id)) > 0:
                return forbidden("template already in use")

            # remove template cache and storage
            self.cache.invalidate(self.__get_template_cache_key(template_id))
            self.storage.delete(template.url)

            # remove record in DB
            self.db.delete_all_objects_by(HackathonTemplateRel, template_id=template.id)
            self.db.delete_object(template)

            return ok("delete template success")
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("delete template failed")

    def __init__(self):
        pass

    def __create_or_update_template(self, template_content):
        """Internally create template

        Save template to storage and then insert into DB

        :type template_content: TemplateContent
        :param template_content: instance of TemplateContent that owns the full content of a template
        """
        context = self.__save_template_to_storage(template_content)
        if not context:
            return internal_server_error("save template failed")

        return self.__save_template_to_database(template_content, context)

    def __save_template_to_storage(self, template_content):
        """save template to a file in storage whose type is configurable

        :type template_content: TemplateContent
        :param template_content: instance of TemplateContent that owns the full content of a template

        :return: context if no exception raised
        """
        try:
            file_name = '%s.js' % template_content.name
            context = Context(
                file_name=file_name,
                file_type=FILE_TYPE.TEMPLATE,
                content=template_content.to_dict()
            )
            self.log.debug("save=ing template as file [%s]" % file_name)
            context = self.storage.save(context)
            return context
        except Exception as ex:
            self.log.error(ex)
            return None

    def __save_template_to_database(self, template_content, context):
        """save template date to db

        According to the args , find out whether it is ought to insert or update a record

        :type template_content: TemplateContent
        :param template_content: instance of TemplateContent that owns the full content of a template

        :type context: Context
        :param context: the context that return from self.__save_template_to_storage

        :return: if raised exception return InternalServerError else return nothing

        """
        template = self.db.find_first_object_by(Template, name=template_content.name)
        try:
            provider = self.__get_provider_from_template_dic(template_content)
            if template is None:
                self.log.debug("insert template info to db: %s" % template_content.name)
                template = self.db.add_object_kwargs(Template,
                                                     name=template_content.name,
                                                     url=context.url,
                                                     local_path=context.get("physical_path"),
                                                     provider=provider,
                                                     creator_id=g.user.id,
                                                     status=TEMPLATE_STATUS.UNCHECKED,
                                                     create_time=self.util.get_now(),
                                                     update_time=self.util.get_now(),
                                                     description=template_content.description,
                                                     virtual_environment_count=len(template_content.units))
            else:
                self.db.update_object(template,
                                      url=context.url,
                                      local_path=context.get("physical_path"),
                                      update_time=self.util.get_now(),
                                      description=template_content.description,
                                      virtual_environment_count=len(template_content.units),
                                      provider=provider)
                self.cache.invalidate(self.__get_template_cache_key(template.id))

            return template.dic()
        except Exception as ex:
            self.log.error(ex)
            raise InternalServerError(description="insert or update record in db failed")

    def __get_provider_from_template_dic(self, template_content):
        """get the provider from template

        :type template_content: TemplateContent
        :param template_content: instance of TemplateContent that owns the full content of a template
        """
        providers = [int(u.provider) for u in template_content.units]
        return providers[0]

    def __get_template_by_name(self, name):
        return self.db.find_first_object_by(Template, name=name)

    def __generate_search_criterion(self, args):
        """generate DB query criterion according to Querystring of request.

        The output will be SQLAlchemy understandable expressions.
        """
        criterion = Template.status != -1
        if 'status' in args and int(args["status"]) >= 0:
            criterion = Template.status == args['status']

        if 'name' in args and len(args['name']) > 0:
            criterion = and_(criterion, Template.name.like('%' + args['name'] + '%'))

        if 'description' in args and len(args['description']) > 0:
            criterion = and_(criterion, Template.description.like('%' + args['description'] + '%'))

        return criterion

    def __get_template_cache_key(self, template_id):
        return "__template__%d__" % template_id

    def __load_template_content(self, args):
        """ Convert dict of template content into TemplateContent object

        :type args: dict
        :param args: args to create a template

        :rtype: TemplateContent
        :return: instance of TemplateContent
        """
        self.__validate_template_content(args)
        return TemplateContent.from_dict(args)

    def __validate_template_content(self, args):
        """ validate args when creating a template

        :type args: dict
        :param args: args to create a template

        :return: if validate passed return nothing else raised a BadRequest exception

        """
        if TEMPLATE.TEMPLATE_NAME not in args:
            raise BadRequest(description="template name invalid")

        if TEMPLATE.DESCRIPTION not in args:
            raise BadRequest(description="template description invalid")

        if TEMPLATE.VIRTUAL_ENVIRONMENTS not in args:
            raise BadRequest(description="template virtual_environments invalid")

        if len(args[TEMPLATE.VIRTUAL_ENVIRONMENTS]) == 0:
            raise BadRequest(description="template virtual_environments invalid")

        for unit in args[TEMPLATE.VIRTUAL_ENVIRONMENTS]:
            if TEMPLATE.VIRTUAL_ENVIRONMENT_PROVIDER not in unit:
                raise BadRequest(description="virtual_environment provider invalid")

    def __get_template_from_request(self):
        """ get template dic from http post request

        get file from request , then json load it to a dic

        :return: template dic , if load file failed raise BadRequest exception
        """
        for file_name in request.files:
            try:
                template = json.load(request.files[file_name])
                self.log.debug("create template from file: %r" % template)
                return template
            except Exception as ex:
                self.log.error(ex)
                raise BadRequest(description="invalid template file")
