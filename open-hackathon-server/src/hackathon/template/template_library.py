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
import uuid
import requests

from sqlalchemy import and_
from flask import g, request

from hackathon import Component, RequiredFeature, Context
from hackathon.database import Template, Experiment, HackathonTemplateRel
from hackathon.hackathon_response import not_found, ok, internal_server_error, forbidden
from hackathon.constants import FILE_TYPE, TEMPLATE_STATUS
from template_constants import TEMPLATE
from docker_template_unit import DockerTemplateUnit
from docker_template import DockerTemplate

__all__ = ["TemplateLibrary"]


class TemplateLibrary(Component):
    """Component to manage templates"""

    cache_manager = RequiredFeature("cache")
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

    def search_template(self, args):
        """Search template by status, name or description"""
        criterion = self.__generate_search_criterions(args)
        templates = self.db.find_all_objects(Template, criterion)
        return [t.dic() for t in templates]

    def load_template(self, template):
        """load template into memory either from a local cache path or an remote uri
        load template from local file > from from azure
        :param template:
        :return:
        """

        def get_template():
            local_path = template.local_path
            if local_path is not None and isfile(local_path):
                with open(local_path) as template_file:
                    return json.load(template_file)
            else:
                try:
                    req = requests.get(template.url)
                    return json.loads(req.content)
                except Exception as e:
                    self.log.warn("Fail to load template from remote file %s" % template.url)
                    self.log.error(e)
                    return None

        return self.cache_manager.get_cache(key=self.__get_template_cache_key(template.id), createfunc=get_template)

    def create_template(self, args):
        """ create template

        The whole logic contains 3 main steps:
        1 : args validate
        2 : parse args and save to storage
        3 : save to database

        :type args: dict
        :param args: description of the template that you want to create

        :return:
        """
        self.__check_create_args(args)
        context = self.__save_template_to_storage(args)
        if not context:
            return internal_server_error("save tempplate failed")
        self.log.debug("create template: %r" % args)
        self.__save_template_to_database(args, context)
        return ok("create template success")

    def create_template_by_file(self):
        """create a template by a whole template file

        The whole logic contains 4 main steps:
        1 : get template dic from PostRequest
        2 : args validate
        3 : parse args and save to storage
        4 : save to database

        :return:

        """
        template = self.__get_template_from_request()
        self.__check_create_args(template)
        context = self.__save_template_to_storage(template)
        if not context:
            return internal_server_error("save template failed")
        self.__save_template_to_database(template, context)
        return ok("create template success")

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
        self.__check_update_args(args)
        context = self.__save_template_to_storage(args)
        if not context:
            return internal_server_error("save tempplate failed")
        self.__save_template_to_database(args, context)
        return ok("update template success")

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
            self.cache_manager.invalidate(self.__get_template_cache_key(template_id))
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

    def __save_template_to_storage(self, args):
        """save template to a file in storage which is chosen by configuration

        Parse out template from args and merge with default template value
        Then generate a file name, and save it to a physical file in storage

        :type args: dict
        :param args: description of template

        :return: context if no exception raised
        """
        try:
            docker_template_units = [DockerTemplateUnit(ve) for ve in args[TEMPLATE.VIRTUAL_ENVIRONMENTS]]
            docker_template = DockerTemplate(args[TEMPLATE.TEMPLATE_NAME],
                                             args[TEMPLATE.DESCRIPTION],
                                             docker_template_units)
            file_name = '%s-%s-%s.js' % (g.user.name, args[TEMPLATE.TEMPLATE_NAME], str(uuid.uuid1())[0:8])
            context = Context(
                file_name=file_name,
                file_type=FILE_TYPE.TEMPLATE,
                content=docker_template.dic
            )
            self.log.debug("save=ing template as file [%s]" % file_name)
            context = self.storage.save(context)
            return context
        except Exception as ex:
            self.log.error(ex)
            return None

    def __save_template_to_database(self, args, context):
        """save template date to db

        According to the args , find out whether it is ought to insert or update a record

        :type args : dict
        :param args: description of template that you want to insert to DB

        :type context: Context
        :param context: the context that return from self.__save_template_to_storage

        :return: if raised exception return InternalServerError else return nothing

        """
        template = self.db.find_first_object_by(Template, name=args[TEMPLATE.TEMPLATE_NAME])
        try:
            # insert record
            if template is None:
                self.log.debug("create template: %r" % args)
                provider = self.__get_provider_from_template_dic(args)
                self.db.add_object_kwargs(Template,
                                          name=args[TEMPLATE.TEMPLATE_NAME],
                                          url=context.url,
                                          local_path=context.get("physical_path"),
                                          provider=provider,
                                          creator_id=g.user.id,
                                          status=TEMPLATE_STATUS.UNCHECKED,
                                          create_time=self.util.get_now(),
                                          update_time=self.util.get_now(),
                                          description=args[TEMPLATE.DESCRIPTION],
                                          virtual_environment_count=len(args[TEMPLATE.VIRTUAL_ENVIRONMENTS]))
            else:
                # update record
                self.db.update_object(template,
                                      url=context.url,
                                      local_path=context.get("physical_path"),
                                      update_time=self.util.get_now(),
                                      description=args[TEMPLATE.DESCRIPTION],
                                      virtual_environment_count=len(args[TEMPLATE.VIRTUAL_ENVIRONMENTS]))
                self.cache_manager.invalidate(self.__get_template_cache_key(template.id))
        except Exception as ex:
            self.log.error(ex)
            raise InternalServerError(description="insert or update record in db failed")

    def __get_provider_from_template_dic(self, template):
        """get the provider from template

        :type template: dict
        :param template: dict object of template

        :return: provider value , if not exist in template return None
        """
        try:
            if TEMPLATE.VIRTUAL_ENVIRONMENTS_PROVIDER in template:
                return template[TEMPLATE.VIRTUAL_ENVIRONMENTS_PROVIDER]
            return template[TEMPLATE.VIRTUAL_ENVIRONMENTS][0][TEMPLATE.VIRTUAL_ENVIRONMENTS]
        except Exception as e:
            self.log.error(e)
            return None

    def __check_update_args(self, args):
        """ validate args when updating a template

        :type args: dict
        :param args: description for a template that you want to update

        :return: if validate passed return nothing else raised a BadRequest or Forbidden exceptions

        """
        self.__check_create_args(args)
        template = self.db.find_first_object_by(Template, name=args[TEMPLATE.TEMPLATE_NAME])
        if template is None:
            raise BadRequest("template does not exist")
        # user can only modify the template which created by himself except super admin
        if g.user.id != template.creator_id and not self.user_manager.is_super_admin(g.user):
            raise Forbidden()

    def __generate_search_criterions(self, args):
        """generate DB query criterion according to Querystring of request.

        The output will be SQLAlchemy understandable expressions.
        """
        criterion = Template.status != -1
        if 'status' in args:
            criterion = and_(criterion, Template.status == args['status'])

        if 'name' in args and len(args['name']) > 0:
            criterion = and_(criterion, Template.name.like('%' + args['name'] + '%'))

        if 'description' in args and len(args['description']) > 0:
            criterion = and_(criterion, Template.description.like('%' + args['description'] + '%'))

        return criterion

    def __get_template_cache_key(self, template_id):
        return "__template__%d__" % template_id

    def __check_create_args(self, args):
        """ validate args when creating a template

        :type args: dict
        :param args: description for a template that you want to create

        :return: if validate passed return nothing else raised a BadRequest exception

        """
        if TEMPLATE.TEMPLATE_NAME not in args:
            raise BadRequest(description="template name invalid")
        if TEMPLATE.DESCRIPTION not in args:
            raise BadRequest(description="template description invalid")
        if TEMPLATE.VIRTUAL_ENVIRONMENTS_PROVIDER not in args:
            raise BadRequest(description="template provider invalid")
        if TEMPLATE.VIRTUAL_ENVIRONMENTS not in args:
            raise BadRequest(description="template virtual_environments invalid")

    def __get_template_from_request(self):
        """ get template dic from http post request

        get file from request , then json load it to a dic

        :return: template dic , if load file failed raise BadRequest exception
        """
        for file_name in request.files:
            try:
                template = json.load(request.files[file_name])
                self.log.debug("create template: %r" % template)
                return template
            except Exception as ex:
                self.log.error(ex)
                raise BadRequest(description="invalid template file")
