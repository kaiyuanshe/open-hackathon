# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

import sys

from hackathon.hazure.cloud_service_adapter import CloudServiceAdapter

sys.path.append("..")

from compiler.ast import flatten
from threading import Lock
import json
import requests
from datetime import timedelta

from hackathon import RequiredFeature, Component, Context
from hackathon.hmongo.models import DockerContainer, DockerHostServer
from hackathon.constants import HEALTH, HEALTH_STATUS, HACKATHON_CONFIG, CLOUD_PROVIDER


class HostedDockerFormation(Component):
    hackathon_template_manager = RequiredFeature("hackathon_template_manager")
    hackathon_manager = RequiredFeature("hackathon_manager")
    expr_manager = RequiredFeature("expr_manager")
    """
    Docker resource management based on docker remote api v1.18
    Host resource are required. Azure key required in case of azure.
    """
    application_json = {'content-type': 'application/json'}
    docker_host_manager = RequiredFeature("docker_host_manager")

    def __init__(self):
        self.lock = Lock()

    def report_health(self):
        """Report health of DockerHostServers

        :rtype: dict
        :return health status item of docker. OK when all servers running, Warning if some of them working,
            Error if no server running
        """
        try:
            # TODO skip hackathons that are offline or ended
            hosts = self.db.find_all_objects(DockerHostServer)
            alive = 0
            for host in hosts:
                if self.ping(host):
                    alive += 1
            if alive == len(hosts):
                return {
                    HEALTH.STATUS: HEALTH_STATUS.OK
                }
            elif alive > 0:
                return {
                    HEALTH.STATUS: HEALTH_STATUS.WARNING,
                    HEALTH.DESCRIPTION: 'at least one docker host servers are down'
                }
            else:
                return {
                    HEALTH.STATUS: HEALTH_STATUS.ERROR,
                    HEALTH.DESCRIPTION: 'all docker host servers are down'
                }
        except Exception as e:
            return {
                HEALTH.STATUS: HEALTH_STATUS.ERROR,
                HEALTH.DESCRIPTION: e.message
            }

    def create_container(self, docker_host, container_config, container_name):
        """
        only create a container, in this step, we cannot start a container.
        :param docker_host:
        :param container_config:
        :param container_name:
        :return:
        """
        containers_url = '%s/containers/create?name=%s' % (self.__get_vm_url(docker_host), container_name)
        req = requests.post(containers_url, data=json.dumps(container_config), headers=self.application_json)
        self.log.debug(req.content)
        # todo check the http code first
        container = json.loads(req.content)
        if container is None:
            raise AssertionError("container is none")
        return container

    def start_container(self, docker_host, container_id):
        """
        start a container
        :param docker_host:
        :param container_id:
        :return:
        """
        url = '%s/containers/%s/start' % (self.__get_vm_url(docker_host), container_id)
        req = requests.post(url, headers=self.application_json)
        self.log.debug(req.content)

    def stop_container(self, host_server, container_name):
        """
        delete a container
        :param name:
        :param docker_host:
        :return:
        """
        containers_url = '%s/containers/%s?force=1' % (self.__get_vm_url(host_server), container_name)
        req = requests.delete(containers_url)
        return req

    def pull_image(self, context):
        # todo fix pull_image?
        docker_host_id, image_name, tag = context.docker_host, context.image_name, context.tag
        docker_host = self.db.find_first_object_by(DockerHostServer, id=docker_host_id)
        if not docker_host:
            return
        pull_image_url = self.__get_vm_url(docker_host) + "/images/create?fromImage=" + image_name + '&tag=' + tag
        self.log.debug(" send request to pull image:" + pull_image_url)
        return requests.post(pull_image_url)

    def get_pulled_images(self, docker_host):
        get_images_url = self.__get_vm_url(docker_host) + "/images/json?all=0"
        current_images_info = json.loads(requests.get(get_images_url).content)  # [{},{},{}]
        current_images_tags = map(lambda x: x['RepoTags'], current_images_info)  # [[],[],[]]
        return flatten(current_images_tags)  # [ imange:tag, image:tag ]

    def ensure_images(self):
        hackathons = self.hackathon_manager.get_online_hackathons()
        map(lambda h: self.__ensure_images_for_hackathon(h), hackathons)

    def is_container_running(self, docker_container):
        """check container's running status on docker host

        if status is Running or Restarting returns True , else returns False

        :type docker_container: DockerContainer
        :param docker_container: the container that you want to check

        :type: bool
        :return True: the container running status is running or restarting , else returns False

        """
        docker_host = docker_container.host_server
        if docker_host:
            container_info = self.__get_container_info_by_container_id(docker_host, docker_container.container_id)
            if container_info is None:
                return False
            return container_info['State']['Running'] or container_info['State']['Restarting']
        else:
            return False

    def ping(self, docker_host, timeout=20):
        """Ping docker host to check running status

        :type docker_host : DockerHostServer
        :param docker_host: the hots that you want to check docker service running status

        :type: bool
        :return: True: running status is OK, else return False

        """
        try:
            ping_url = '%s/_ping' % self.__get_vm_url(docker_host)
            req = requests.get(ping_url, timeout=timeout)
            return req.status_code == 200 and req.content == 'OK'
        except Exception as e:
            self.log.error(e)
            return False

    def get_containers_detail_by_ve(self, virtual_environment):
        """Get all containers' detail from "Database" filtered by related virtual_environment

        :rtype: dict
        :return: get the info of all containers

        """
        container = virtual_environment.docker_container
        if container:
            return self.util.make_serializable(container.to_mongo().to_dict())
        return {}

    def list_containers(self, docker_host, timeout=20):
        """
        return: json(as list form) through "Docker restful API"
        """
        containers_url = '%s/containers/json' % self.__get_vm_url(docker_host)
        req = requests.get(containers_url, timeout=timeout)
        self.log.debug(req.content)
        return self.util.convert(json.loads(req.content))

    def get_container_by_name(self, container_name, docker_host):
        containers = self.list_containers(docker_host)
        return next((c for c in containers if container_name in c["Names"] or '/' + container_name in c["Names"]), None)

    # --------------------------------------------- helper function ---------------------------------------------#

    def __get_vm_url(self, docker_host):
        return 'http://%s:%d' % (docker_host.public_dns, docker_host.public_docker_api_port)

    def __get_schedule_job_id(self, hackathon):
        return "pull_images_for_hackathon_%s" % hackathon.id

    def __ensure_images_for_hackathon(self, hackathon):
        # only ensure those alauda is disabled
        if hackathon.config.get(HACKATHON_CONFIG.CLOUD_PROVIDER) == CLOUD_PROVIDER.ALAUDA:
            self.log.debug("schedule job of hackathon '%s(%d)' removed for alauda enabled" %
                           (hackathon.name, hackathon.id))
            self.scheduler.remove_job(self.__get_schedule_job_id(hackathon))
            return

        job_id = self.__get_schedule_job_id(hackathon)
        job_exist = self.scheduler.has_job(job_id)
        if hackathon.event_end_time < self.util.get_now():
            if job_exist:
                self.scheduler.remove_job(job_id)
            return
        else:
            if job_exist:
                self.log.debug("job %s existed" % job_id)
            else:
                self.log.debug(
                    "adding schedule job to ensure images for hackathon %s" % hackathon.name)
                next_run_time = self.util.get_now() + timedelta(seconds=3)
                context = Context(hackathon_id=hackathon.id)
                self.scheduler.add_interval(feature="hackathon_template_manager",
                                            method="pull_images_for_hackathon",
                                            id=job_id,
                                            context=context,
                                            next_run_time=next_run_time,
                                            minutes=60)

    def __get_container_info_by_container_id(self, docker_host, container_id):
        """get a container info by container_id from a docker host

        :param: the docker host which you want to search container from

        :type container_id: str|unicode
        :param as a parameter that you want to search container though docker remote API

        :return dic object of the container info if not None
        """
        try:
            get_container_url = self.__get_vm_url(docker_host) + "/containers/%s/json?all=0" % container_id
            req = requests.get(get_container_url)
            if 300 > req.status_code >= 200:
                container_info = json.loads(req.content)
                return container_info
            return None
        except Exception as ex:
            self.log.error(ex)
            return None
