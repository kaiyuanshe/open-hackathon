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

from hackathon.database.models import (
    Template,
    DockerHostServer,
)
from hackathon.database import (
    db_adapter,
)
from hackathon.hack import (
    hack_manager,
)
from hackathon.hackathon_response import (
    not_found,
    bad_request,
    internal_server_error,
    ok,
)
from hackathon.functions import (
    get_now,
)
from hackathon.enum import (
    TEMPLATE_STATUS,
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
from hackathon.scheduler import (
    scheduler,
)
from hackathon.azureformation.fileService import (
    file_service,
)
from hackathon.functions import (
    safe_get_config,
)
from hackathon.log import (
    log,
)
from flask import (
    g,
)
from datetime import (
    timedelta,
)
import uuid
import requests
import json


class TemplateManager(object):
    def get_created_template_list(self, hackathon_name):
        """
        Get created template list of given hackathon
        :param hackathon_name:
        :return:
        """
        hackathon = hack_manager.get_hackathon_by_name(hackathon_name)
        if hackathon is None:
            return not_found('hackathon [%s] not found' % hackathon_name)
        created_templates = db_adapter.find_all_objects_by(Template,
                                                           hackathon_id=hackathon.id,
                                                           status=TEMPLATE_STATUS.CREATED)
        data = []
        for created_template in created_templates:
            dic = created_template.dic()
            dic['data'] = json.load(file(created_template.url))
            data.append(dic)
        return data

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
        file_name = '%s-%s-%s.js' % (g.hackathon.name, args[BaseTemplate.EXPR_NAME], str(uuid.uuid1())[0:8])
        # create template step 2 : parse args and trans to file
        url = self.__save_args_to_file(args, file_name)
        if url is None:
            return internal_server_error("save template as local file failed")
        # create template step 3 : upload template file to Azure
        azure_url = self.__upload_template_to_azure(url, file_name)
        if azure_url is None:
            return internal_server_error("upload template file failed")
        # create template step 4 : insert into DB
        log.debug("create template: %r" % args)
        db_adapter.add_object_kwargs(Template,
                                     name=args[BaseTemplate.EXPR_NAME],
                                     url=url,
                                     azure_url=azure_url,
                                     provider=args[BaseTemplate.VIRTUAL_ENVIRONMENTS_PROVIDER],
                                     creator_id=g.user.id,
                                     status=TEMPLATE_STATUS.CREATED,
                                     create_time=get_now(),
                                     update_time=get_now(),
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
        file_name = '%s-%s-%s.js' % (g.hackathon.name, args[BaseTemplate.EXPR_NAME], str(uuid.uuid1())[0:8])
        # update template step 2 : parse args and trans to file
        url = self.__save_args_to_file(args, file_name)
        if url is None:
            return internal_server_error("save template as local file failed")
        # update template step 3 : upload template file to Azure
        azure_url = self.__upload_template_to_azure(url, file_name)
        if azure_url is None:
            return internal_server_error("upload template file failed")
        # update template step 4 : update DB
        log.debug("update template: %r" % args)
        template = return_info
        db_adapter.update_object(template,
                                 url=url,
                                 azure_url=azure_url,
                                 update_time=get_now(),
                                 description=args[BaseTemplate.DESCRIPTION],
                                 virtual_environment_count=len(args[BaseTemplate.VIRTUAL_ENVIRONMENTS]))
        return ok("update template success")

    def delete_template(self, id):
        log.debug("delete template [%d]" % id)
        try:
            template = db_adapter.get_object(Template, id)
            db_adapter.update_object(template,
                                     status=TEMPLATE_STATUS.DELETED,
                                     update_time=get_now())
            return ok("delete template success")
        except Exception as ex:
            log.error(ex)
            return internal_server_error("delete template fail")

    def pull_images(self, image_name):
        hosts = db_adapter.find_all_objects(DockerHostServer, DockerHostServer.hackathon_id == g.hackathon.id)
        docker_host_api = map(lambda x: x.public_docker_api_port, hosts)
        for api in docker_host_api:
            url = api + "/images/create?fromImage=" + image_name
            exec_time = get_now() + timedelta(seconds=2)
            log.debug(" send request to pull image:" + url)
            # use requests.post instead of post_to_remote, because req.contect can not be json.loads()
            scheduler.add_job(requests.post, 'date', run_date=exec_time, args=[url])

    # ---------------------------------------- helper functions ---------------------------------------- #

    def __check_create_args(self, args):
        if BaseTemplate.EXPR_NAME not in args \
                or BaseTemplate.DESCRIPTION not in args \
                or BaseTemplate.VIRTUAL_ENVIRONMENTS_PROVIDER not in args \
                or BaseTemplate.VIRTUAL_ENVIRONMENTS not in args:
            return False, bad_request("template args invalid")
        if db_adapter.count_by(Template, name=args[BaseTemplate.EXPR_NAME]) > 0:
            return False, bad_request("template already exists")
        return True, "pass"

    def __save_args_to_file(self, args, file_name):
        try:
            docker_template_units = [DockerTemplateUnit(ve) for ve in args[BaseTemplate.VIRTUAL_ENVIRONMENTS]]
            docker_template = DockerTemplate(args[BaseTemplate.EXPR_NAME],
                                             args[BaseTemplate.DESCRIPTION],
                                             docker_template_units)
            file_path = docker_template.to_file(file_name)
            log.debug("save template as file [%s]" % file_path)
            return file_path
        except Exception as ex:
            log.error(ex)
            return None

    def __upload_template_to_azure(self, path, file_name):
        try:
            template_container = safe_get_config("storage.template_container", "templates")
            return file_service.upload_file_to_azure_from_path(path, template_container, file_name)
        except Exception as ex:
            log.error(ex)
            return None

    def __check_update_args(self, args):
        if BaseTemplate.EXPR_NAME not in args \
                or BaseTemplate.DESCRIPTION not in args \
                or BaseTemplate.VIRTUAL_ENVIRONMENTS_PROVIDER not in args \
                or BaseTemplate.VIRTUAL_ENVIRONMENTS not in args:
            return False, bad_request("template args invalid")
        template = db_adapter.find_first_object_by(Template, name=args[BaseTemplate.EXPR_NAME])
        if template is None:
            return False, bad_request("template not exists")
        return True, template


template_manager = TemplateManager()

# template_manager.create_template({
# "expr_name": "test",
# "virtual_environments": [
# {}, {}
# ]
# })