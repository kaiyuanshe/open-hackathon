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

import os, sys
import uuid

sys.path.append("..")
from hackathon.database.models import Template, DockerHostServer
from hackathon.hackathon_response import bad_request, not_found, internal_server_error, ok
from datetime import timedelta
import time
from hackathon.enum import TEMPLATE_STATUS
from hackathon.template.docker_template_unit import DockerTemplateUnit
from hackathon.template.docker_template import DockerTemplate
from hackathon.template.base_template import BaseTemplate
from hackathon.scheduler import scheduler
from hackathon import Component, RequiredFeature, g
import json
from compiler.ast import flatten





class TemplateManager(Component):
    hackathon_manager = RequiredFeature("hackathon_manager")
    file_service = RequiredFeature("file_service")
    docker = RequiredFeature("docker")
    base_template = RequiredFeature("base_template")
    docker_template_unit = RequiredFeature("docker_template_unit")

    templates = {}  # template in memory {template.id: template_file_stream}

    def get_template_list(self, hackathon_name):
        hackathon = self.hackathon_manager.get_hackathon_by_name(hackathon_name)
        if hackathon is None:
            return not_found('hackathon not found')
        hack_id = hackathon.id
        templates = self.db.find_all_objects_by(Template, hackathon_id=hack_id)
        return map(lambda u: u.dic(), templates)


    def get_template_by_id(self, id):
        return self.db.find_first_object(Template, Template.id == id)


    def validate_created_args(self, args):
        if "name" not in args:
            return False, bad_request("template name invalid")

        template = self.db.find_first_object(Template, Template.name == args['name'])
        if template is not None:
            return False, bad_request("template aready exist")

        return True, "pass"


    def save_args_to_file(self, args):
        try:
            docker_template_units = [DockerTemplateUnit(ve) for ve in args[BaseTemplate.VIRTUAL_ENVIRONMENTS]]
            docker_template = DockerTemplate(args[BaseTemplate.EXPR_NAME], docker_template_units)
            file_path = docker_template.to_file()
            self.log.debug("save template as file :" + file_path)
            return file_path
        except Exception as ex:
            self.log.error(ex)
            return None


    def upload_template_to_azure(self, path):
        template_container = self.util.safe_get_config("storage.template_container", "templates")

        try:
            real_name = g.hackathon.name + "/" + str(uuid.uuid1())[0:9] + time.strftime("%Y%m%d%H%M%S") + ".js"
            return self.file_service.upload_file_to_azure_from_path(path, template_container, real_name)
        except Exception as ex:
            self.log.error(ex)
            return None


    def create_template(self, args):
        # create template step one : args validate
        status, return_info = self.validate_created_args(args)
        if not status:
            return return_info

        # create template step two : parse args and trans to file
        local_path = self.save_args_to_file(args)
        if local_path is None:
            return internal_server_error("save template as local file failed")

        # create template step Three : upload template file to Azure
        url = self.upload_template_to_azure(local_path)
        if url is None:
            return internal_server_error("upload template file failed")

        # create template step Four : insert into DB
        try:
            self.log.debug("create template: %r" % args)
            args['url'] = url
            args['creator_id'] = g.user.id
            args['update_time'] = self.util.get_now()
            args['hackathon_id'] = g.hackathon.id
            args['status'] = TEMPLATE_STATUS.ONLINE
            return self.db.add_object_kwargs(Template, **args)
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("insert record into template DB failed")


    def update_template(self, args):
        if "name" not in args:
            return bad_request("template name invalid")
        template = self.db.find_first_object(Template, Template.name == args['name'])

        if template is None:
            return bad_request("template doesn't exist")
        try:
            self.log.debug("update template: %r" % args)
            args['update_time'] = self.util.get_now()
            update_items = dict(dict(args).viewitems() - template.dic().viewitems())
            self.log.debug("update a exist hackathon :" + str(args))
            self.db.update_object(template, **update_items)
            return ok("update template success")
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("update template failed :" + ex.message)


    def delete_template(self, id):
        self.log.debug("delete or disable a exist template")
        try:
            template = self.get_template_by_id(id)
            args = {}
            args['status'] = TEMPLATE_STATUS.OFFLINE
            args['update_time'] = self.util.get_now()
            self.db.update_object(template, args)
            return ok("delete or disable template success")
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("disable or delete failed")


    # load template priority : from memory > from local file > from from azure
    def load_template(self, template):
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

    # get template_dic from memroty
    def __load_template_from_memory(self, template_id):
        if template_id not in self.templates:
            return None
        else:
            return self.templates[template_id]

    # get template_dic from local file
    def __load_template_from_local_file(self, template_id, local_url):
        if not os.path.exists(local_url):
            return None
        else:
            template_dic = json.loads(file(local_url))
            self.templates[template_id] = template_dic
            return template_dic

    # get template_dic from azure storage
    def __load_template_from_azure(self, template_id, local_url, azure_url):
        container_name = self.util.safe_get_config("storage.template_container", "templates")
        if self.file_service.download_file_from_azure(container_name, azure_url, local_url) is not None:
            return self.__load_template_from_local_file(template_id, local_url)
        return None


    def pull_images_for_hackathon(self, hackathon):
        hosts = self.db.find_all_objects(DockerHostServer, DockerHostServer.hackathon_id == hackathon.id)
        docker_host_api = map(lambda x: x.public_docker_api_port, hosts)
        # loop to get every docker host
        for api in docker_host_api:
            templates = hackathon.templates
            images = map(lambda x: self.__get_images_from_template(x), templates)
            expected_images = flatten(images)
            download_images = self.__get_undownloaded_images_on_docker_host(api, expected_images)
            for dl_image in download_images:
                exec_time = self.util.get_now() + timedelta(seconds=2)
                scheduler.add_job(self.docker.pull_image, 'pullimage', run_date=exec_time, args=[api, dl_image])


    def __get_images_from_template(self, template):
        template_dic = self.load_template(template)
        virtuals = template_dic[self.base_template.VIRTUAL_ENVIRONMENTS]
        images = map(lambda x: x[self.docker_template_unit.IMAGE], virtuals)
        return images


    def __get_undownloaded_images_on_docker_host(self, api, *expected_images):
        images = []
        get_images_url = api + "/images/json?all=0"
        current_images_info = json.loads(self.util.get_remote(get_images_url))  #[{},{},{}]
        current_images_tags = map(lambda x: json.load(x)['RepoTags'], current_images_info)  #[[],[],[]]
        for ex_image in expected_images:
            exist = False

            for cur_image_tag in current_images_tags:
                if ex_image in cur_image_tag:
                    exist = True
                    break

            if not exist:
                images.append(ex_image)

        return images


# template_manager.create_template({
# "expr_name": "test",
# "virtual_environments": [
# {}, {}
# ]
# })

