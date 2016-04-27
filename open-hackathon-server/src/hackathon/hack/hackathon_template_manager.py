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

from hackathon.hmongo.models import Template

from hackathon import Component, RequiredFeature, Context
from hackathon.constants import VE_PROVIDER, TEMPLATE_STATUS
from hackathon.hackathon_response import not_found, internal_server_error

__all__ = ["HackathonTemplateManager"]


class HackathonTemplateManager(Component):
    """Components to manage hackathon-template relationships"""

    team_manager = RequiredFeature("team_manager")
    hackathon_manager = RequiredFeature("hackathon_manager")
    template_library = RequiredFeature("template_library")
    hosted_docker = RequiredFeature("hosted_docker")

    def add_template_to_hackathon(self, template_id):
        try:
            template = Template.objects(id=template_id).first()

            if template is None:
                return not_found("template does not exist")

            if not (template in g.hackathon.templates):
                g.hackathon.templates.append(template)
                g.hackathon.save()

            return self.get_templates_with_detail_by_hackathon(g.hackathon)

        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("add a hackathon template rel record faild")

    def delete_template_from_hackathon(self, template_id):
        template = Template.objects(id=template_id).first()
        if template is None:
            return not_found("template does not exist")

        if template in g.hackathon.templates:
            g.hackathon.templates.remove(template)
            g.hackathon.save()

        # self.db.delete_object(htr)
        return self.get_templates_with_detail_by_hackathon(g.hackathon)

    def get_templates_with_detail_by_hackathon(self, hackathon):
        """Get all templates as well as its details used by certain hackathon"""

        return [t.dic() for t in hackathon.templates]

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
        templates = self.__get_templates_for_pull(hackathon_id)
        images = map(lambda x: self.__get_images_from_template(x), templates)
        images_to_pull = flatten(images)

        self.log.debug('expected images: %s on hackathon: %s' % (images_to_pull, hackathon_id))
        # get all docker host server on hackathon
        hosts = self.db.find_all_objects_by(DockerHostServer, hackathon_id=hackathon_id)
        # loop to get every docker host
        for docker_host in hosts:
            download_images = self.__get_undownloaded_images_on_docker_host(docker_host, images_to_pull)
            self.log.debug('need to pull images: %s on host: %s' % (download_images, docker_host.vm_name))
            for dl_image in download_images:
                image = dl_image.split(':')[0]
                tag = dl_image.split(':')[1]
                context = Context(image=image,
                                  tag=tag,
                                  docker_host=docker_host.id)
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
        templates = team.templates
        if len(templates) == 0:
            # get template for the hackathon
            templates = hackathon.templates

        data = []
        for template in templates:
            content = self.template_library.load_template(template)
            data.append((template, content))
        return data

    # template may have multiple images
    def __get_images_from_template(self, template):
        template_content = self.template_library.load_template(template)
        docker_units = filter(lambda u: u.provider == VE_PROVIDER.DOCKER, template_content.units)
        docker_images = [du.get_image_with_tag() for du in docker_units]
        return docker_images

    def __get_templates_for_pull(self, hackathon_id):
        htrs = self.db.find_all_objects_by(HackathonTemplateRel, hackathon_id=hackathon_id)
        templates = [h.template for h in htrs]
        templates = filter(lambda t: t.provider == VE_PROVIDER.DOCKER and t.status == TEMPLATE_STATUS.CHECK_PASS,
                           templates)
        return templates

    def __get_undownloaded_images_on_docker_host(self, docker_host, expected_images):
        images = []
        current_images = self.hosted_docker.get_pulled_images(docker_host)
        self.log.debug('already exist images: %s on host: %s' % (current_images, docker_host.vm_name))
        for ex_image in expected_images:
            if ex_image not in current_images:
                images.append(ex_image)
        return flatten(images)
