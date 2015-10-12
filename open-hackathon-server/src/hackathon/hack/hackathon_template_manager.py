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
from compiler.ast import flatten

from flask import g

from hackathon import Component, RequiredFeature, Context
from hackathon.database import HackathonTemplateRel, Template, DockerHostServer
from hackathon.template import TEMPLATE, DOCKER_UNIT
from hackathon.constants import VE_PROVIDER, TEMPLATE_STATUS
from hackathon.hackathon_response import ok, not_found, internal_server_error

__all__ = ["HackathonTemplateManager"]


class HackathonTemplateManager(Component):
    """Components to manage hackaton-template relationships"""

    team_manager = RequiredFeature("team_manager")
    hackathon_manager = RequiredFeature("hackathon_manager")
    template_library = RequiredFeature("template_library")
    hosted_docker = RequiredFeature("hosted_docker")

    def add_template_to_hackathon(self, template_id, team_id=-1):
        template = self.db.find_first_object_by(Template, id=template_id)
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
        self.db.delete_all_objects_by(HackathonTemplateRel,
                                      template_id=template_id,
                                      hackathon_id=g.hackathon.id,
                                      team_id=team_id)
        # self.db.delete_object(htr)
        return ok()

    def get_templates_by_hackathon_id(self, hackathon_id):
        """Get all templates used by certain hackathon"""
        return self.db.find_all_objects_by(HackathonTemplateRel, hackathon_id=hackathon_id)

    def get_templates_with_detail_by_hackathon(self, hackathon_id):
        """Get all templates as well as its details used by certain hackathon"""
        templates = self.get_templates_by_hackathon_id(hackathon_id)
        templates_with_details = [self.__get_template_detail(t) for t in templates]
        return templates_with_details

    def get_user_templates(self, user, hackathon):
        template_list = self.__get_templates_by_user(user, hackathon)
        settings = []
        for template, content in template_list:
            template_units = []
            for unit in content.units:
                template_units.append({
                    'name': unit.get_name(),
                    'type': unit.get_type(),
                    'description': unit.get_description(),
                })
            settings.append({
                'name': template.name,
                'description': template.description,
                'units': template_units,
            })
        return settings

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

    def __init__(self):
        pass

    def __get_template_detail(self, rel):
        """Return Template detail as well as hackathon-template relation"""
        ret = rel.dic()
        ret["template"] = rel.template.dic()
        return ret

    def __get_templates_by_user(self, user, hackathon):
        team = self.team_manager.get_team_by_user_and_hackathon(user, hackathon)
        if team is None:
            return []

        # get templates of the team
        htrs = self.db.find_all_objects_by(HackathonTemplateRel, hackathon_id=hackathon.id, team_id=team.id)
        if len(htrs) == 0:
            # get template for the hackathon
            htrs = self.db.find_all_objects_by(HackathonTemplateRel, hackathon_id=hackathon.id, team_id=-1)

        templates = map(lambda x: x.template, htrs)
        data = []
        for template in templates:
            content = self.template_library.load_template(template)
            data.append((template, content))
        return data

    # template may have multiple images
    def __get_images_from_template(self, template):
        template_dic = self.template_library.load_template(template)
        ves = template_dic[TEMPLATE.VIRTUAL_ENVIRONMENTS]
        images = map(lambda x: x[DOCKER_UNIT.IMAGE], ves)
        return images  # [image:tag, image:tag]

    def __get_templates_for_pull(self, hackathon_id):
        hackathon = self.hackathon_manager.get_hackathon_by_id(hackathon_id)
        htrs = hackathon.hackathon_template_rels
        template_ids = map(lambda x: x.template.id, htrs)
        templates = self.db.find_all_objects(Template,
                                             Template.id.in_(template_ids),
                                             Template.provider == VE_PROVIDER.DOCKER,
                                             Template.status == TEMPLATE_STATUS.CHECK_PASS)
        return templates

    def __get_undownloaded_images_on_docker_host(self, docker_host, expected_images):
        images = []
        current_images = self.hosted_docker.get_pulled_images(docker_host)
        self.log.debug('already exist images: %s on host: %s' % (current_images, docker_host.vm_name))
        for ex_image in expected_images:
            if ex_image not in current_images:
                images.append(ex_image)
        return flatten(images)
