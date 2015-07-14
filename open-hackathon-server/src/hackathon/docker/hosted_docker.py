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

sys.path.append("..")

from hackathon import (
    RequiredFeature,
    Component,
    Context,
)
from hackathon.database.models import (
    Experiment,
    DockerContainer,
    HackathonAzureKey,
    PortBinding,
    DockerHostServer,
)
from hackathon.constants import (
    EStatus,
    PortBindingType,
    VEStatus,
)
from compiler.ast import (
    flatten,
)
from threading import (
    Lock,
)
from hackathon.template.docker_template_unit import (
    DockerTemplateUnit,
)
from hackathon.azureformation.endpoint import (
    Endpoint
)
from docker_formation_base import (
    DockerFormationBase,
)
from hackathon.azureformation.service import (
    Service,
)
from hackathon.hackathon_response import (
    internal_server_error
)
from hackathon.constants import (
    HEALTH_STATE,
)
import json
import requests
from datetime import timedelta



class HostedDockerFormation(DockerFormationBase, Component):
    template_manager = RequiredFeature("template_manager")
    hackathon_manager = RequiredFeature("hackathon_manager")
    scheduler = RequiredFeature("scheduler")
    """
    Docker resource management based on docker remote api v1.18
    Host resource are required. Azure key required in case of azure.
    """
    application_json = {'content-type': 'application/json'}
    host_ports = []
    host_port_max_num = 30
    docker_host_manager = RequiredFeature("docker_host_manager")

    def __init__(self):
        self.lock = Lock()

    def health(self):
        """
        Ping docker service in docker host
        :return:
        """
        try:
            hosts = self.db.find_all_objects(DockerHostServer)
            alive = 0
            for host in hosts:
                if self._ping(host):
                    alive += 1
            if alive == len(hosts):
                return {
                    "status": HEALTH_STATE.OK
                }
            elif alive > 0:
                return {
                    "status": HEALTH_STATE.WARNING,
                    "description": 'at least one docker host servers are down'
                }
            else:
                return {
                    "status": HEALTH_STATE.ERROR,
                    "description": 'all docker host servers are down'
                }
        except Exception as e:
            return {
                "status": HEALTH_STATE.ERROR,
                "description": e.message
            }

    def get_available_host_port(self, docker_host, private_port):
        """
        We use double operation to ensure ports not conflicted, first we get ports from host machine, but in multiple
        threads situation, the interval between two requests is too short, maybe the first thread do not get port
        ended, so the host machine don't update ports in time, thus the second thread may get the same port.
        To avoid this condition, we use static variable host_ports to cache the latest host_port_max_num ports.
        Every thread visit variable host_ports is synchronized.
        To save space, we will release the ports if the number over host_port_max_num.
        :param docker_host:
        :param private_port:
        :return:
        """
        self.log.debug("try to assign docker port %d on server %r" % (private_port, docker_host))
        containers = self.__containers_info(docker_host)
        host_ports = flatten(map(lambda p: p['Ports'], containers))

        # todo if azure return -1
        def sub(port):
            return port["PublicPort"] if "PublicPort" in port else -1

        host_public_ports = map(lambda x: sub(x), host_ports)
        return self.__get_available_host_port(host_public_ports, private_port)

    def stop(self, name, **kwargs):
        """
        stop a container
        :param name: container's name
        :param docker_host: host machine where container running
        :return:
        """
        container = kwargs["container"]
        expr_id = kwargs["expr_id"]
        docker_host = self.docker_host_manager.get_host_server_by_id(container.host_server_id)
        if self.__get_container(name, docker_host) is not None:
            containers_url = '%s/containers/%s/stop' % (self.get_vm_url(docker_host), name)
            req = requests.post(containers_url)
            self.log.debug(req.content)
        self.__stop_container(expr_id, container, docker_host)

    def delete(self, name, **kwargs):
        """
        delete a container
        :param name:
        :param docker_host:
        :return:
        """
        container = kwargs["container"]
        expr_id = kwargs["expr_id"]
        docker_host = self.docker_host_manager.get_host_server_by_id(container.host_server_id)
        containers_url = '%s/containers/%s?force=1' % (self.get_vm_url(docker_host), name)
        req = requests.delete(containers_url)
        self.log.debug(req.content)

        self.__stop_container(expr_id, container, docker_host)

    def start(self, unit, **kwargs):
        """
        In this function, we create a container and then start a container
        :param unit: docker template unit
        :param docker_host:
        :return:
        """
        virtual_environment = kwargs["virtual_environment"]
        hackathon = kwargs["hackathon"]
        experiment = kwargs["experiment"]
        container_name = unit.get_name()
        host_server = self.docker_host_manager.get_available_docker_host(1, hackathon)

        container = DockerContainer(experiment,
                                    name=container_name,
                                    host_server_id=host_server.id,
                                    virtual_environment=virtual_environment,
                                    image=unit.get_image_with_tag())
        self.db.add_object(container)
        self.db.commit()

        # port binding
        ps = map(lambda p:
                 [p.port_from, p.port_to],
                 self.__assign_ports(experiment, host_server, virtual_environment, unit.get_ports()))

        # guacamole config
        guacamole = unit.get_remote()
        port_cfg = filter(lambda p:
                          p[DockerTemplateUnit.PORTS_PORT] == guacamole[DockerTemplateUnit.REMOTE_PORT],
                          unit.get_ports())
        if len(port_cfg) > 0:
            gc = {
                "displayname": container_name,
                "name": container_name,
                "protocol": guacamole[DockerTemplateUnit.REMOTE_PROTOCOL],
                "hostname": host_server.public_ip,
                "port": port_cfg[0]["public_port"]
            }
            if DockerTemplateUnit.REMOTE_USERNAME in guacamole:
                gc["username"] = guacamole[DockerTemplateUnit.REMOTE_USERNAME]
            if DockerTemplateUnit.REMOTE_PASSWORD in guacamole:
                gc["password"] = guacamole[DockerTemplateUnit.REMOTE_PASSWORD]
            # save guacamole config into DB
            virtual_environment.remote_paras = json.dumps(gc)

        exist = self.__get_container(container_name, host_server)
        if exist is not None:
            container.container_id = exist["Id"]
            host_server.container_count += 1
            self.db.commit()
        else:
            container_config = unit.get_container_config()
            # create container
            try:
                container_create_result = self.__create(host_server, container_config, container_name)
            except Exception as e:
                self.log.error(e)
                self.log.error("container %s fail to create" % container_name)
                return None
            container.container_id = container_create_result["Id"]
            # start container
            try:
                self.__start(host_server, container_create_result["Id"])
                host_server.container_count += 1
                self.db.commit()
            except Exception as e:
                self.log.error(e)
                self.log.error("container %s fail to start" % container["Id"])
                return None
            # check
            if self.__get_container(container_name, host_server) is None:
                self.log.error(
                    "container %s has started, but can not find it in containers' info, maybe it exited again."
                    % container_name)
                return None

        self.log.debug("starting container %s is ended ... " % container_name)
        virtual_environment.status = VEStatus.RUNNING
        self.db.commit()
        return container

    def get_vm_url(self, docker_host):
        return 'http://%s:%d' % (docker_host.public_dns, docker_host.public_docker_api_port)

    def pull_image(self, context):
        docker_host, image_name, tag = context.docker_host, context.image_name, context.tag
        pull_image_url = self.get_vm_url(docker_host) + "/images/create?fromImage=" + image_name + '&tag=' + tag
        self.log.debug(" send request to pull image:" + pull_image_url)
        return requests.post(pull_image_url)

    def get_pulled_images(self, docker_host):
        get_images_url = self.get_vm_url(docker_host) + "/images/json?all=0"
        current_images_info = json.loads(self.util.get_remote(get_images_url))  # [{},{},{}]
        current_images_tags = map(lambda x: x['RepoTags'], current_images_info)  # [[],[],[]]
        return flatten(current_images_tags)  # [ imange:tag, image:tag ]

    def ensure_images(self):
        hackathons = self.hackathon_manager.get_online_hackathons()
        map(lambda h: self.__ensure_images_for_hackathon(h), hackathons)

    # --------------------------------------------- helper function ---------------------------------------------#

    def __name_match(self, id, lists):
        for list in lists:
            if id in list:
                return True
        return False

    def __get_schedule_job_id(self, hackathon):
        return "pull_images_for_hackathon_%s" % hackathon.id

    def __ensure_images_for_hackathon(self, hackathon):
        # only ensure those alauda is disabled
        if hackathon.is_alauda_enabled():
            self.log.debug("schedule job of hackathon '%s(%d)' removed for alauda enabled" %
                           (hackathon.name, hackathon.id))
            self.scheduler.remove_job(self.__get_schedule_job_id(hackathon))
            return

        self.log.debug("adding schedule job to ensure images for hackathon [%d]%s" % (hackathon.id, hackathon.name))
        next_run_time = self.util.get_now() + timedelta(seconds=3)
        context = Context(hackathon_id=hackathon.id)
        self.scheduler.add_interval(feature="template_manager",
                                    method="pull_images_for_hackathon",
                                    id=self.__get_schedule_job_id(hackathon),
                                    context=context,
                                    next_run_time=next_run_time,
                                    minutes=60)

    def __get_vm_url(self, docker_host):
        return 'http://%s:%d' % (docker_host.public_dns, docker_host.public_docker_api_port)

    def _ping(self, docker_host):
        """
        Ping docker service in docker host
        :param docker_host:
        :return:
        """
        try:
            ping_url = '%s/_ping' % self.__get_vm_url(docker_host)
            req = requests.get(ping_url)
            self.log.debug(req.content)
            return req.status_code == 200 and req.content == 'OK'
        except Exception as e:
            self.log.error(e)
            return False

    def __clear_ports_cache(self):
        """
        cache ports, if ports' number more than host_port_max_num, release the ports.
        But if there is a thread apply new ports, we will do this operation in the next loop.
        Because the host machine do not update the ports information,
        if we release ports now, the new ports will be lost.
        :return:
        """
        num = self.db.count(Experiment, Experiment.status == EStatus.STARTING)
        if num > 0:
            self.log.debug("there are %d experiment is starting, host ports will updated in next loop" % num)
            return
        self.log.debug("-----release ports cache successfully------")
        self.host_ports = []

    def __stop_container(self, expr_id, container, docker_host):
        self.__release_ports(expr_id, docker_host)
        docker_host.container_count -= 1
        if docker_host.container_count < 0:
            docker_host.container_count = 0
        self.db.commit()

    def __containers_info(self, docker_host):
        containers_url = '%s/containers/json' % self.get_vm_url(docker_host)
        req = requests.get(containers_url)
        self.log.debug(req.content)
        return self.util.convert(json.loads(req.content))

    def __get_available_host_port(self, port_bindings, port):
        """
        simple lock mechanism, visit static variable ports synchronize, because port_bindings is not in real-time,
        so we should cache the latest ports, when the cache ports number is more than host_port_max_num,
        we will release it to save space.
        :param port_bindings:
        :param port:
        :return:
        """
        self.lock.acquire()
        try:
            host_port = port + 10000
            while host_port in port_bindings or host_port in self.host_ports:
                host_port += 1
            if host_port >= 65535:
                self.log.error("port used up on this host server")
                raise Exception("no port available")
            if len(self.host_ports) >= self.host_port_max_num:
                self.__clear_ports_cache()
            self.host_ports.append(host_port)
            self.log.debug("host_port is %d " % host_port)
            return host_port
        finally:
            self.lock.release()

    def __get_container(self, name, docker_host):
        containers = self.__containers_info(docker_host)
        return next((c for c in containers if name in c["Names"] or '/' + name in c["Names"]), None)

    def __create(self, docker_host, container_config, container_name):
        """
        only create a container, in this step, we cannot start a container.
        :param docker_host:
        :param container_config:
        :param container_name:
        :return:
        """
        containers_url = '%s/containers/create?name=%s' % (self.get_vm_url(docker_host), container_name)
        req = requests.post(containers_url, data=json.dumps(container_config), headers=self.application_json)
        self.log.debug(req.content)
        container = json.loads(req.content)
        if container is None:
            raise AssertionError("container is none")
        return container

    def __start(self, docker_host, container_id):
        """
        start a container
        :param docker_host:
        :param container_id:
        :return:
        """
        url = '%s/containers/%s/start' % (self.get_vm_url(docker_host), container_id)
        req = requests.post(url, headers=self.application_json)
        self.log.debug(req.content)

    def __get_available_public_ports(self, expr_id, host_server, host_ports):
        self.log.debug("starting to get azure ports")
        ep = Endpoint(Service(self.load_azure_key_id(expr_id)))
        host_server_name = host_server.vm_name
        host_server_dns = host_server.public_dns.split('.')[0]
        public_endpoints = ep.assign_public_endpoints(host_server_dns, 'Production', host_server_name, host_ports)
        if not isinstance(public_endpoints, list):
            self.log.debug("failed to get public ports")
            return internal_server_error('cannot get public ports')
        self.log.debug("public ports : %s" % public_endpoints)
        return public_endpoints

    def load_azure_key_id(self, expr_id):
        expr = self.db.get_object(Experiment, expr_id)
        hak = self.db.find_first_object_by(HackathonAzureKey, hackathon_id=expr.hackathon_id)
        return hak.azure_key_id

    def __assign_ports(self, expr, host_server, ve, port_cfg):
        """
        assign ports from host server
        :param expr:
        :param host_server:
        :param ve:
        :param port_cfg:
        :return:
        """
        # get 'host_port'
        map(lambda p:
            p.update(
                {DockerTemplateUnit.PORTS_HOST_PORT: self.get_available_host_port(host_server, p[
                    DockerTemplateUnit.PORTS_PORT])}
            ),
            port_cfg)

        # get 'public' cfg
        public_ports_cfg = filter(lambda p: DockerTemplateUnit.PORTS_PUBLIC in p, port_cfg)
        host_ports = [u[DockerTemplateUnit.PORTS_HOST_PORT] for u in public_ports_cfg]
        if self.util.safe_get_config("environment", "prod") == "local":
            map(lambda cfg: cfg.update({DockerTemplateUnit.PORTS_PUBLIC_PORT: cfg[DockerTemplateUnit.PORTS_HOST_PORT]}),
                public_ports_cfg)
        else:
            public_ports = self.__get_available_public_ports(expr.id, host_server, host_ports)
            for i in range(len(public_ports_cfg)):
                public_ports_cfg[i][DockerTemplateUnit.PORTS_PUBLIC_PORT] = public_ports[i]

        binding_dockers = []

        # update port binding
        for public_cfg in public_ports_cfg:
            binding_cloud_service = PortBinding(name=public_cfg[DockerTemplateUnit.PORTS_NAME],
                                                port_from=public_cfg[DockerTemplateUnit.PORTS_PUBLIC_PORT],
                                                port_to=public_cfg[DockerTemplateUnit.PORTS_HOST_PORT],
                                                binding_type=PortBindingType.CLOUD_SERVICE,
                                                binding_resource_id=host_server.id,
                                                virtual_environment=ve,
                                                experiment=expr,
                                                url=public_cfg[DockerTemplateUnit.PORTS_URL]
                                                if DockerTemplateUnit.PORTS_URL in public_cfg else None)
            binding_docker = PortBinding(name=public_cfg[DockerTemplateUnit.PORTS_NAME],
                                         port_from=public_cfg[DockerTemplateUnit.PORTS_HOST_PORT],
                                         port_to=public_cfg[DockerTemplateUnit.PORTS_PORT],
                                         binding_type=PortBindingType.DOCKER,
                                         binding_resource_id=host_server.id,
                                         virtual_environment=ve,
                                         experiment=expr)
            binding_dockers.append(binding_docker)
            self.db.add_object(binding_cloud_service)
            self.db.add_object(binding_docker)
        self.db.commit()

        local_ports_cfg = filter(lambda p: DockerTemplateUnit.PORTS_PUBLIC not in p, port_cfg)
        for local_cfg in local_ports_cfg:
            port_binding = PortBinding(name=local_cfg[DockerTemplateUnit.PORTS_NAME],
                                       port_from=local_cfg[DockerTemplateUnit.PORTS_HOST_PORT],
                                       port_to=local_cfg[DockerTemplateUnit.PORTS_PORT],
                                       binding_type=PortBindingType.DOCKER,
                                       binding_resource_id=host_server.id,
                                       virtual_environment=ve,
                                       experiment=expr)
            binding_dockers.append(port_binding)
            self.db.add_object(port_binding)
        self.db.commit()
        return binding_dockers

    def __release_ports(self, expr_id, host_server):
        """
        release the specified experiment's ports
        """
        self.log.debug("Begin to release ports: expr_id: %d, host_server: %r" % (expr_id, host_server))
        ports_binding = self.db.find_all_objects_by(PortBinding, experiment_id=expr_id)
        if ports_binding is not None:
            docker_binding = filter(
                lambda u: self.util.safe_get_config("environment", "prod") != "local" and u.binding_type == 1,
                ports_binding)
            ports_to = [d.port_to for d in docker_binding]
            if len(ports_to) != 0:
                self.__release_public_ports(expr_id, host_server, ports_to)
            for port in ports_binding:
                self.db.delete_object(port)
            self.db.commit()
        self.log.debug("End to release ports: expr_id: %d, host_server: %r" % (expr_id, host_server))

    def __release_public_ports(self, expr_id, host_server, host_ports):
        ep = Endpoint(Service(self.load_azure_key_id(expr_id)))
        host_server_name = host_server.vm_name
        host_server_dns = host_server.public_dns.split('.')[0]
        self.log.debug("starting to release ports ... ")
        ep.release_public_endpoints(host_server_dns, 'Production', host_server_name, host_ports)
