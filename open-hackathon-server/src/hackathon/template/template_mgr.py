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

import os
import sys
import uuid
import json

sys.path.append("..")

from compiler.ast import (
    flatten,
)
from hackathon.database.models import (
    Template,
    DockerHostServer,
    HackathonTemplateRel,
    Experiment
)
from hackathon.hackathon_response import (
    not_found,
    bad_request,
    internal_server_error,
    ok,
    access_denied
)
from hackathon.enum import (
    TEMPLATE_STATUS,
    VEProvider,
)
from hackathon.template.docker_template_unit import (
    DockerTemplateUnit,
)
from hackathon.template.docker_template import (
    DockerTemplate,
)
from hackathon.template.base_template import (
    BaseTemplate,
)

from hackathon import (
    Component,
    RequiredFeature,
    Context
)
from flask import g
from sqlalchemy import (
    and_
)


class TemplateManager(Component):
    hackathon_manager = RequiredFeature("hackathon_manager")
    file_service = RequiredFeature("file_service")
    docker = RequiredFeature("docker")
    scheduler = RequiredFeature("scheduler")
    user_manager = RequiredFeature("user_manager")
    team_manager = RequiredFeature("team_manager")

    templates = {}  # template in memory {template.id: template_file_dic}

    def get_template_by_id(self, id):
        return self.db.find_first_object(Template, id=id)

    def get_template_by_name(self, template_name):
        return self.db.find_first_object_by(Template, name=template_name)

    def get_templates_by_hackathon_id(self, hackathon_id):
        htrs = self.db.find_all_objects_by(HackathonTemplateRel, hackathon_id=hackathon_id)
        return map(lambda x: x.template, htrs)

    def get_template_list(self, **kwargs):
        condition = self.__get_filter_condition(**kwargs)
        return self.db.find_all_objects(Template, condition)

    def get_user_templates(self, user, hackathon):
        template_list = self.__get_templates_by_user(user, hackathon)
        settings = []
        for template in template_list:
            template_units = []
            for ve in template['data'][BaseTemplate.VIRTUAL_ENVIRONMENTS]:
                template_units.append({
                    'name': ve[DockerTemplateUnit.NAME],
                    'type': ve[DockerTemplateUnit.TYPE] if DockerTemplateUnit.TYPE in ve else "",
                    'description': ve[DockerTemplateUnit.DESCRIPTION] if DockerTemplateUnit.DESCRIPTION in ve else "",
                })
            settings.append({
                'name': template['data'][BaseTemplate.TEMPLATE_NAME],
                'description': template['data'][BaseTemplate.DESCRIPTION] if BaseTemplate.DESCRIPTION in template[
                    'data'] else "",
                'units': template_units,
            })
        return settings

    def create_template(self, args):
        # create template step 1 : args validate
        status, return_info = self.__check_create_args(args)
        if not status:
            return return_info
        file_name = '%s-%s-%s.js' % (g.user.name, args[BaseTemplate.TEMPLATE_NAME], str(uuid.uuid1())[0:8])
        # create template step 2 : parse args and trans to file
        url = self.__save_args_to_file(args, file_name)
        if url is None:
            return internal_server_error("save template as local file failed")
        # create template step 3 : upload template file to Azure
        azure_url = self.__upload_template_to_azure(url, file_name)
        if azure_url is None:
            return internal_server_error("upload template file failed")
        # create template step 4 : insert into DB
        self.log.debug("create template: %r" % args)
        self.db.add_object_kwargs(Template,
                                  name=args[BaseTemplate.TEMPLATE_NAME],
                                  url=url,
                                  azure_url=azure_url,
                                  provider=args[BaseTemplate.VIRTUAL_ENVIRONMENTS_PROVIDER],
                                  creator_id=g.user.id,
                                  status=TEMPLATE_STATUS.UNCHECK,
                                  create_time=self.util.get_now(),
                                  update_time=self.util.get_now(),
                                  description=args[BaseTemplate.DESCRIPTION],
                                  virtual_environment_count=len(args[BaseTemplate.VIRTUAL_ENVIRONMENTS]))
        return ok("create template success")

    def update_template(self, args):
        """
        Update template according to post args
        :param args:
        :return:
        """
        # update template step 1 : args validate
        status, return_info = self.__check_update_args(args)
        if not status:
            return return_info
        file_name = '%s-%s-%s.js' % (g.hackathon.name, args[BaseTemplate.TEMPLATE_NAME], str(uuid.uuid1())[0:8])
        # update template step 2 : parse args and trans to file
        url = self.__save_args_to_file(args, file_name)
        if url is None:
            return internal_server_error("save template as local file failed")
        # update template step 3 : upload template file to Azure
        azure_url = self.__upload_template_to_azure(url, file_name)
        if azure_url is None:
            return internal_server_error("upload template file failed")
        # update template step 4 : update DB
        self.log.debug("update template: %r" % args)
        template = return_info
        self.db.update_object(template,
                              url=url,
                              azure_url=azure_url,
                              update_time=self.util.get_now(),
                              description=args[BaseTemplate.DESCRIPTION],
                              virtual_environment_count=len(args[BaseTemplate.VIRTUAL_ENVIRONMENTS]))
        # refresh template in memory after update
        self.__load_template_from_local_file(template.id, url)
        return ok("update template success")

    def delete_template(self, id):
        self.log.debug("delete template [%d]" % id)
        try:
            template = self.db.get_object(Template, id)
            if template is None:
                return ok("already removed")
            # user can only delete the template which created by himself except super admin
            if g.user.id != template.creator_id and not self.user_manager.is_super_admin(g.user):
                return access_denied()
            if len(self.db.find_all_objects_by(Experiment, template_id=id)) > 0:
                return access_denied("template already in use")

            # remove template cache , localfile, azurefile
            self.templates.pop(template.id, '')
            if os.path.exists(template.url):
                os.remove(template.url)
            container_name = self.util.safe_get_config("storage.template_container", "templates")
            blob_name = template.azure_url.split("/")[-1]
            self.file_service.delete_file_from_azure(container_name, blob_name)

            # remove record in DB
            self.db.delete_all_objects_by(HackathonTemplateRel, template_id=template.id)
            self.db.delete_object(template)

            return ok("delete template success")
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("delete template failed")

    def load_template(self, template):
        """
        load template priority : from memory > from local file > from from azure
        :param template:
        :return:
        """
        template_id = template.id
        dic_from_memory = self.__load_template_from_memory(template_id)
        if dic_from_memory is not None:
            return dic_from_memory

        local_url = template.url
        dic_from_local = self.__load_template_from_local_file(template_id, local_url)
        if dic_from_local is not None:
            return dic_from_local

        azure_url = template.azure_url
        dic_from_azure = self.__load_template_from_azure(template_id, local_url, azure_url)
        if dic_from_azure is not None:
            return dic_from_azure

        return None

    def pull_images_for_hackathon(self, context):
        hackathon_id = context.hackathon_id
        # get templates which is online and provided by docker
        templates = self.__get_templates_for_pull(hackathon_id)
        # get expected images on hackathons' templates
        images = map(lambda x: self.__get_images_from_template(x), templates)
        expected_images = flatten(images)
        self.log.debug('expected images: %s on hackathon: %s' % (expected_images, hackathon_id))
        # get all docker host server on hackathon
        hosts = self.db.find_all_objects_by(DockerHostServer, hackathon_id=hackathon_id)
        # loop to get every docker host
        for docker_host in hosts:
            download_images = self.__get_undownloaded_images_on_docker_host(docker_host, expected_images)
            self.log.debug('need to pull images: %s on host: %s' % (download_images, docker_host.vm_name))
            for dl_image in download_images:
                image = dl_image.split(':')[0]
                tag = dl_image.split(':')[1]
                context = Context(image=image,
                                  tag=tag,
                                  docker_host=docker_host)
                self.scheduler.add_once(feature="hosted_docker",
                                        method="pull_image",
                                        context=context,
                                        seconds=3)

    def add_template_to_hackathon(self, template_name, team_id=-1):
        template = self.get_template_by_name(template_name)
        if template is None:
            return not_found("template does not exist")
        htr = self.db.find_first_object_by(HackathonTemplateRel,
                                           template_id=template.id,
                                           hackathon_id=g.hackathon.id,
                                           team_id=team_id)
        if htr is not None:
            return ok("already exist")
        try:
            self.db.add_object_kwargs(HackathonTemplateRel,
                                      hackathon_id=g.hackathon.id,
                                      template_id=template.id,
                                      team_id=team_id,
                                      update_time=self.util.get_now())
            return ok()
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("add a hackathon template rel record faild")

    def delete_template_from_hackathon(self, template_id, team_id=-1):
        htr = self.db.find_first_object_by(HackathonTemplateRel,
                                           template_id=template_id,
                                           hackathon_id=g.hackathon.id,
                                           team_id=team_id)
        if htr is None:
            return ok("already removed")
        try:
            self.db.delete_object(htr)
            return ok()
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("delete hackathon template rel record faild")

    # ---------------------------------------- helper functions ---------------------------------------- #

    def __check_create_args(self, args):
        if BaseTemplate.TEMPLATE_NAME not in args \
                or BaseTemplate.DESCRIPTION not in args \
                or BaseTemplate.VIRTUAL_ENVIRONMENTS_PROVIDER not in args \
                or BaseTemplate.VIRTUAL_ENVIRONMENTS not in args:
            return False, bad_request("template args invalid")
        if self.db.count_by(Template, name=args[BaseTemplate.TEMPLATE_NAME]) > 0:
            return False, bad_request("template already exists")
        return True, "pass"

    def __save_args_to_file(self, args, file_name):
        try:
            docker_template_units = [DockerTemplateUnit(ve) for ve in args[BaseTemplate.VIRTUAL_ENVIRONMENTS]]
            docker_template = DockerTemplate(args[BaseTemplate.TEMPLATE_NAME],
                                             args[BaseTemplate.DESCRIPTION],
                                             docker_template_units)
            file_path = docker_template.to_file(file_name)
            self.log.debug("save template as file [%s]" % file_path)
            return file_path
        except Exception as ex:
            self.log.error(ex)
            return None

    def __upload_template_to_azure(self, path, file_name):
        try:
            template_container = self.util.safe_get_config("storage.template_container", "templates")
            return self.file_service.upload_file_to_azure_from_path(path, template_container, file_name)
        except Exception as ex:
            self.log.error(ex)
            return None

    def __check_update_args(self, args):
        if BaseTemplate.TEMPLATE_NAME not in args \
                or BaseTemplate.DESCRIPTION not in args \
                or BaseTemplate.VIRTUAL_ENVIRONMENTS_PROVIDER not in args \
                or BaseTemplate.VIRTUAL_ENVIRONMENTS not in args:
            return False, bad_request("template args invalid")
        template = self.db.find_first_object_by(Template, name=args[BaseTemplate.TEMPLATE_NAME])
        if template is None:
            return False, bad_request("template does not exist")
        # user can only modify the template which created by himself except super admin
        if g.user.id != template.creator_id and not self.user_manager.is_super_admin(g.user):
            return False, access_denied()
        return True, template

    def __load_template_from_memory(self, template_id):
        """
        get template_dic from memory
        :param template_id:
        :return:
        """
        if template_id is None or template_id not in self.templates:
            return None
        else:
            return self.templates[template_id]

    def __load_template_from_local_file(self, template_id, local_url):
        """
        get template_dic from local file
        :param template_id:
        :param local_url:
        :return:
        """
        if local_url is None or not os.path.exists(local_url):
            return None
        else:
            template_dic = json.load(file(local_url))
            self.templates[template_id] = template_dic
            return template_dic

    def __load_template_from_azure(self, template_id, local_url, azure_url):
        """
        get template_dic from azure storage
        :param template_id:
        :param local_url:
        :param azure_url:
        :return:
        """
        if azure_url is not None:
            if self.file_service.download_file_from_azure(azure_url, local_url) is not None:
                return self.__load_template_from_local_file(template_id, local_url)
        return None

    def __get_templates_by_user(self, user, hackathon):
        team = self.team_manager.get_team_by_user_and_hackathon(user, hackathon)
        if team is None:
            return []
        # get template from team
        htrs = self.db.find_all_objects(HackathonTemplateRel, hackathon_id=hackathon.id, team_id=team.id)
        if len(htrs) == 0:
            # get template from hackathon
            htrs = self.db.find_all_objects(HackathonTemplateRel, hackathon_id=hackathon.id, team_id=-1)

        templates = map(lambda x: x.template, htrs)
        data = []
        for template in templates:
            dic = template.dic()
            dic['data'] = self.load_template(template)
            data.append(dic)
        return data

    def __get_templates_for_pull(self, hackathon_id):
        hackathon = self.hackathon_manager.get_hackathon_by_id(hackathon_id)
        htrs = hackathon.hackathon_template_rels
        template_ids = map(lambda x: x.template.id, htrs)
        templates = self.db.find_all_objects(Template,
                                             Template.id.in_(template_ids),
                                             Template.provider == VEProvider.Docker,
                                             Template.status == TEMPLATE_STATUS.CHECK_PASS)
        return templates

    # template may have multiple images
    def __get_images_from_template(self, template):
        template_dic = self.load_template(template)
        ves = template_dic[BaseTemplate.VIRTUAL_ENVIRONMENTS]
        images = map(lambda x: x[DockerTemplateUnit.IMAGE], ves)
        return images  # [image:tag, image:tag]

    def __get_undownloaded_images_on_docker_host(self, docker_host, expected_images):
        images = []
        current_images = self.docker.get_pulled_images(docker_host)
        self.log.debug('already exist images: %s on host: %s' % (current_images, docker_host.vm_name))
        for ex_image in expected_images:
            if ex_image not in current_images:
                images.append(ex_image)
        return flatten(images)

    def __get_filter_condition(self, **kwargs):
        """parse args and transfer to condition that can be used to query in DB

        :type  kwargs: dict
        :param kwargs: filter conditions

        :return: condition for query in DB
        """
        condition = Template.status != -1
        if kwargs['status'] is not None:
            condition = and_(condition, Template.status == kwargs['status'])

        if kwargs['name'] is not None:
            condition = and_(condition, Template.name.like('%'+kwargs['name']+'%'))

        if kwargs['description'] is not None:
            condition = and_(condition, Template.description.like('%'+kwargs['description']+'%'))

        return condition
