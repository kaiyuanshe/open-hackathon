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

from datetime import (
    timedelta,
)
from compiler.ast import (
    flatten,
)
from hackathon.database.models import (
    Template,
    DockerHostServer,
)
from hackathon.hackathon_response import (
    not_found,
    bad_request,
    internal_server_error,
    ok,
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
)
from flask import g

class TemplateManager(Component):
    hackathon_manager = RequiredFeature("hackathon_manager")
    file_service = RequiredFeature("file_service")
    docker = RequiredFeature("docker")

    templates = {}  # template in memory {template.id: template_file_stream}

    def get_created_template_list(self, hackathon_name):
        """
        Get created template list of given hackathon
        :param hackathon_name:
        :return:
        """
        hackathon = self.hackathon_manager.get_hackathon_by_name(hackathon_name)
        if hackathon is None:
            return not_found('hackathon [%s] not found' % hackathon_name)
        created_templates = self.db.find_all_objects_by(Template,
                                                        hackathon_id=hackathon.id,
                                                        status=TEMPLATE_STATUS.CREATED)
        data = []
        for created_template in created_templates:
            dic = created_template.dic()
            dic['data'] = self.load_template(created_template)
            data.append(dic)
        return data

    def get_template_settings(self, hackathon_name):
        template_list = self.get_created_template_list(hackathon_name)
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
        """
        Create template according to post args
        :param args:
        :return:
        """
        # create template step 1 : args validate
        status, return_info = self.__check_create_args(args)
        if not status:
            return return_info
        file_name = '%s-%s-%s.js' % (g.hackathon.name, args[BaseTemplate.TEMPLATE_NAME], str(uuid.uuid1())[0:8])
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
                                  status=TEMPLATE_STATUS.CREATED,
                                  create_time=self.util.get_now(),
                                  update_time=self.util.get_now(),
                                  description=args[BaseTemplate.DESCRIPTION],
                                  virtual_environment_count=len(args[BaseTemplate.VIRTUAL_ENVIRONMENTS]),
                                  hackathon_id=g.hackathon.id)
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
            self.db.update_object(template,
                                  status=TEMPLATE_STATUS.DELETED,
                                  update_time=self.util.get_now())
            return ok("delete template success")
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("delete template fail")

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

    def pull_images_for_hackathon(self, hackathon):
        # get expected images on hackathon
        templates = self.db.find_all_objects_by(Template,
                                                hackathon_id=hackathon.id,
                                                provider=VEProvider.Docker,
                                                status=TEMPLATE_STATUS.CREATED)
        images = map(lambda x: self.__get_images_from_template(x), templates)
        expected_images = flatten(images)
        self.log.debug('expected images: %s on hackathon: %s' % (expected_images, hackathon.name))
        # get all docker host server on hackathon
        hosts = self.db.find_all_objects_by(DockerHostServer, hackathon_id=hackathon.id)
        # loop to get every docker host
        for docker_host in hosts:
            download_images = self.__get_undownloaded_images_on_docker_host(docker_host, expected_images)
            self.log.debug('need to pull images: %s on host: %s' % (download_images, docker_host.vm_name))
            for dl_image in download_images:
                exec_time = self.util.get_now() + timedelta(seconds=3)
                image = dl_image.split(':')[0]
                tag = dl_image.split(':')[1]
                #todo docker pull
                # scheduler.add_job(docker_pull_image, 'date', run_date=exec_time, args=[docker_host, image, tag])

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
            return False, bad_request("template not exists")
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
