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
from threading import Lock

from docker_expr_starter import DockerExprStarter
from hackathon import RequiredFeature, Context
from hackathon.hmongo.models import Hackathon, Experiment, DockerContainer, PortBinding, DockerHostServer, AzureKey
from hackathon.constants import DHS_QUERY_STATE, EStatus, AVMStatus, VERemoteProvider, VEStatus
from hackathon.hazure import VirtualMachineAdapter
from hackathon.template import DOCKER_UNIT
from hackathon.hazure.utils import find_unassigned_endpoints, add_endpoint_to_network_config, \
    delete_endpoint_from_network_config

FEATURE = "azure_docker"
IN_PROGRESS = 'InProgress'
SUCCEEDED = 'Succeeded'
MAX_TRIAL = 20
TRIAL_INTERVAL_SECONDS = 10
DEPLOYMENT_SLOT = "Production"

__all__ = ["AzureHostedDockerStarter"]


class AzureHostedDockerStarter(DockerExprStarter):
    docker = RequiredFeature("hosted_docker_proxy")
    docker_host_manager = RequiredFeature("docker_host_manager")
    host_ports = []
    host_port_max_num = 30

    def __init__(self):
        self.lock = Lock()

    def get_docker_host_server(self, context):
        hackathon = Hackathon.objects(id=context.hackathon_id).no_dereference().first()
        try:
            host_resp = self.docker_host_manager.get_available_docker_host(hackathon)
        except Exception as e:
            self.log.error(e)
            host_resp = Context(state=DHS_QUERY_STATE.ONGOING)

        context.trial = context.get("trial", 0) + 1
        if host_resp.state == DHS_QUERY_STATE.SUCCESS:
            # assign ports
            self.__assign_ports(context, host_resp.docker_host_server)
        elif host_resp.state == DHS_QUERY_STATE.ONGOING and context.trial < 20:
            # tried up to 20 times
            self.log.debug("host servers are all busy, %d times tried, will retry in 3 seconds" % context.trial)
            self.scheduler.add_once(FEATURE, "get_docker_host_server", context, seconds=3)
        else:
            self.log.error("no available host server")
            self._on_virtual_environment_failed(context)

    def query_network_config_status(self, context):
        vm_adapter = self.__get_azure_vm_adapter(context)
        try:
            context.trial = context.get("trial", 0) + 1
            result = vm_adapter.get_operation_status(context.request_id)
            if result.status == IN_PROGRESS and context.trial < MAX_TRIAL:
                self.log.debug('wait for async [%s] loop count [%d]' % (context.request_id, context.trial))
                self.scheduler.add_once(FEATURE, "query_network_config_status", context, seconds=TRIAL_INTERVAL_SECONDS)
            elif result.status == SUCCEEDED:
                context.trial = 0
                self.query_vm_status(context)
            elif context.trial >= MAX_TRIAL:
                self.log.error("timeout when configure network")
                self._on_virtual_environment_failed(context)
            else:
                self.log.error(vars(result))
                if result.error:
                    self.log.error(result.error.code)
                    self.log.error(vars(result.error))
                self.log.error('Asynchronous operation did not succeed.')
                self._on_virtual_environment_failed(context)
        except Exception as e:
            self.log.error(e)
            self.scheduler.add_once(FEATURE, "query_network_config_status", context, seconds=TRIAL_INTERVAL_SECONDS)

    def query_vm_status(self, context):
        vm_adapter = self.__get_azure_vm_adapter(context)
        try:
            context.trial = context.get("trial", 0) + 1
            result = vm_adapter.get_virtual_machine_instance_status(context.cloud_service_name,
                                                                    DEPLOYMENT_SLOT,
                                                                    context.virtual_machine_name)
            if result is None:
                self.log.error("cannot find vm or deployment slot")
                self._on_virtual_environment_failed(context)
            elif result == AVMStatus.READY_ROLE:
                self.__update_virtual_environment_cfg(context)
            elif context.trial > MAX_TRIAL:
                self._on_virtual_environment_failed(context)
            else:
                self.log.debug(
                    'wait for virtual machine [%r] loop count [%d]' % (context.virtual_machine_name, context.trial))
                self.scheduler.add_once(FEATURE, "query_vm_status", context, seconds=TRIAL_INTERVAL_SECONDS)
        except Exception as e:
            self.log.error(e)
            self.scheduler.add_once(FEATURE, "query_vm_status", context, seconds=TRIAL_INTERVAL_SECONDS)

    def _internal_start_virtual_environment(self, context):
        self.get_docker_host_server(context)

    def _get_docker_proxy(self):
        return self.docker

    def _hooks_on_virtual_environment_success(self, context):
        context.trial = 0
        self.enable_guacd_file_transfer(context)

    def enable_guacd_file_transfer(self, context):
        try:
            context.trial += 1
            self._enable_guacd_file_transfer(context)
        except Exception as e:
            self.log.info("enable guacamole file transfer failed count: %d" % context.trial)
            self.log.error(e)
            if context.trial < 20:
                self.scheduler.add_once(FEATURE, "enable_guacd_file_transfer", context, seconds=30)

    def __assign_host_ports(self, context, host_server):
        """assign ports that map a port on docker host server to a port inside docker"""
        unit = context.unit
        # assign host port
        try:
            port_cfg = unit.get_ports()
            for cfg in port_cfg:
                cfg[DOCKER_UNIT.PORTS_HOST_PORT] = self.__get_available_host_port(host_server,
                                                                                  cfg[DOCKER_UNIT.PORTS_PORT])
            context.port_config = port_cfg
            self.__assign_public_ports(context, host_server)
        except Exception as e:
            self.log.error(e)
            self._on_virtual_environment_failed(context)

    def __assign_public_ports(self, context, host_server):
        """assign ports on azure cloud service that map a public port to a port inside certain VM"""
        port_cfg = context.port_config
        context.host_server_id = host_server.id

        if self.util.is_local():
            for cfg in port_cfg:
                cfg[DOCKER_UNIT.PORTS_PUBLIC_PORT] = cfg[DOCKER_UNIT.PORTS_HOST_PORT]
            self.__update_virtual_environment_cfg(context)
        else:
            # configure ports on azure cloud service
            vm_adapter = self.__get_azure_vm_adapter(context)
            virtual_machine_name = host_server.vm_name
            cloud_service_name = host_server.public_dns.split('.')[0]  # cloud_service_name.chinacloudapp.cn

            # filter the port config with "public" True
            self.log.debug("starting to assign azure ports...")
            public_ports_cfg = filter(lambda p: DOCKER_UNIT.PORTS_PUBLIC in p, port_cfg)
            host_ports = [u[DOCKER_UNIT.PORTS_HOST_PORT] for u in public_ports_cfg]

            # get assigned ports of cloud service
            assigned_endpoints = vm_adapter.get_assigned_endpoints(cloud_service_name)
            if not assigned_endpoints:
                self.log.debug('fail to assign endpoints: %s' % cloud_service_name)
                self._on_virtual_environment_failed(context)
                return

            endpoints_to_assign = find_unassigned_endpoints(host_ports, assigned_endpoints)
            # duplication detection for public endpoint
            deployment_name = vm_adapter.get_deployment_name(cloud_service_name, DEPLOYMENT_SLOT)
            network_config = vm_adapter.get_virtual_machine_network_config(cloud_service_name,
                                                                           deployment_name,
                                                                           virtual_machine_name)
            new_network_config = add_endpoint_to_network_config(network_config, endpoints_to_assign, host_ports)
            try:
                result = vm_adapter.update_virtual_machine_network_config(cloud_service_name,
                                                                          deployment_name,
                                                                          virtual_machine_name,
                                                                          new_network_config)
                context.request_id = result.request_id
            except Exception as e:
                self.log.error(e)
                self.log.error('fail to assign endpoints: %s' % endpoints_to_assign)
                self._on_virtual_environment_failed(context)
                return

            updated_config = []
            for cfg in context.port_config:
                if cfg[DOCKER_UNIT.PORTS_HOST_PORT] in host_ports:
                    index = host_ports.index(cfg[DOCKER_UNIT.PORTS_HOST_PORT])
                    cfg[DOCKER_UNIT.PORTS_PUBLIC_PORT] = endpoints_to_assign[index]
                updated_config.append(cfg)
            context.port_config = updated_config

            # query azure to make sure the network config updated
            context.virtual_machine_name = virtual_machine_name
            context.cloud_service_name = cloud_service_name
            context.trial = 0
            self.query_network_config_status(context)

    def __update_virtual_environment_cfg(self, context):
        experiment = Experiment.objects(id=context.experiment_id).no_dereference().first()
        virtual_environment = experiment.virtual_environments.get(name=context.virtual_environment_name)
        host_server = DockerHostServer.objects(id=context.host_server_id).first()

        # azure_key
        if not self.util.is_local():
            experiment.azure_key = AzureKey.objects(id=context.azure_key_id).first()

        # update port binding
        for cfg in context.port_config:
            public_port = cfg[DOCKER_UNIT.PORTS_PUBLIC_PORT] if DOCKER_UNIT.PORTS_PUBLIC_PORT in cfg else None
            port_binding = PortBinding(name=cfg[DOCKER_UNIT.PORTS_NAME],
                                       is_public=bool(cfg[DOCKER_UNIT.PORTS_PUBLIC]),
                                       public_port=public_port,
                                       host_port=cfg[DOCKER_UNIT.PORTS_HOST_PORT],
                                       container_port=cfg[DOCKER_UNIT.PORTS_PORT])
            if DOCKER_UNIT.PORTS_URL in cfg:
                port_binding.url = cfg[DOCKER_UNIT.PORTS_URL]
            virtual_environment.docker_container.port_bindings.append(port_binding)

        # guacamole config
        guacamole = context.unit.get_remote()
        port_cfg = filter(lambda p:
                          p[DOCKER_UNIT.PORTS_PORT] == guacamole[DOCKER_UNIT.REMOTE_PORT],
                          context.port_config)
        if len(port_cfg) > 0:
            virtual_environment.remote_provider = VERemoteProvider.Guacamole
            gc = {
                "displayname": context.virtual_environment_name,
                "name": context.virtual_environment_name,
                "protocol": guacamole[DOCKER_UNIT.REMOTE_PROTOCOL],
                "hostname": host_server.public_ip,
                "port": port_cfg[0][DOCKER_UNIT.PORTS_PUBLIC_PORT],
                "enable-sftp": True
            }
            if DOCKER_UNIT.REMOTE_USERNAME in guacamole:
                gc["username"] = guacamole[DOCKER_UNIT.REMOTE_USERNAME]
            if DOCKER_UNIT.REMOTE_PASSWORD in guacamole:
                gc["password"] = guacamole[DOCKER_UNIT.REMOTE_PASSWORD]

            # save guacamole config into DB
            virtual_environment.remote_paras = gc

        experiment.save()

        # start container
        self.__start_docker_container(context, experiment, host_server)

    def __start_docker_container(self, context, experiment, host_server):
        container_name = context.container_name
        virtual_environment = experiment.virtual_environments.get(name=context.virtual_environment_name)

        exist = self.docker.get_container_by_name(container_name, host_server)
        if exist:
            virtual_environment.docker_container.container_id = exist["Id"]
            experiment.save()
            host_server.container_count += 1
            host_server.save()
        else:
            context.unit.set_ports(context.port_config)
            container_config = context.unit.get_container_config()

            try:
                # create docker container
                container_create_result = self.docker.create_container(host_server, container_config, container_name)
                virtual_environment.docker_container.container_id = container_create_result["Id"]
                experiment.save()

                # start docker container
                self.docker.start_container(host_server, container_create_result["Id"])
                host_server.container_count += 1
                host_server.save()
            except Exception as e:
                self.log.error(e)
                self.log.error("container %s fail to create or start" % container_name)
                # todo looks like the rollback is not valid
                self._on_virtual_environment_failed(context)
                return

            # make sure the container is running
            if self.docker.get_container_by_name(container_name, host_server) is None:
                self.log.error(
                    "container %s has started, but can not find it in containers' info, maybe it exited again."
                    % container_name)
                self._on_virtual_environment_failed(context)
                return

        self.log.debug("starting container %s is successful ... " % container_name)
        virtual_environment.status = VEStatus.RUNNING
        experiment.save()
        self._on_virtual_environment_success(context)

    def __stop_docker_container(self, context, host_server):
        try:
            self.docker.stop_container(host_server, context.container_name)
        except Exception as e:
            self.log.error(e)

        self._on_virtual_environment_stopped(context)

    def __assign_ports(self, context, host_server):
        self.log.debug("try to assign port on server %r" % host_server)
        unit = context.unit
        experiment = Experiment.objects(id=context.experiment_id).no_dereference().first()
        virtual_environment = experiment.virtual_environments.get(name=context.virtual_environment_name)
        container = DockerContainer(name=virtual_environment.name,
                                    image=unit.get_image_with_tag(),
                                    host_server=host_server,
                                    port_bindings=[])
        virtual_environment.docker_container = container
        experiment.save()

        context.container_name = container.name
        self.__assign_host_ports(context, host_server)

    def _stop_virtual_environment(self, virtual_environment, experiment, context):
        if virtual_environment.status == VEStatus.RUNNING:
            if not virtual_environment.docker_container:
                virtual_environment.status = VEStatus.STOPPED
                experiment.save()
                self._on_virtual_environment_stopped(context)
            else:
                try:
                    # release port
                    self._release_port(virtual_environment.docker_container, context)
                except Exception as e:
                    self.log.error(e)
                    self._on_virtual_environment_unexpected_error(context)
        elif virtual_environment.status == VEStatus.STOPPED:
            self._on_virtual_environment_stopped(context)

    def _release_port(self, docker_container, context):
        """
        release the specified experiment's ports.

        We can ignore host port here since it will be release when the container is deleted.
        What we care about is the public ports configured on azure cloud service
        """

        host_server = docker_container.host_server
        if self.util.is_local():
            context.container_name = docker_container.name
            self.__stop_docker_container(context, host_server)
            return

        self.log.debug("Begin to release ports: host_server: %r" % host_server)
        vm_adapter = self.__get_azure_vm_adapter(context)
        virtual_machine_name = host_server.vm_name
        cloud_service_name = host_server.public_dns.split('.')[0]  # cloud_service_name.chinacloudapp.cn
        deployment_name = vm_adapter.get_deployment_name(cloud_service_name, DEPLOYMENT_SLOT)

        # current network config
        network_config = vm_adapter.get_virtual_machine_network_config(cloud_service_name,
                                                                       deployment_name,
                                                                       virtual_machine_name)
        host_ports = [p.host_port for p in docker_container.port_bindings]
        new_network_config = delete_endpoint_from_network_config(network_config, host_ports)
        result = vm_adapter.update_virtual_machine_network_config(cloud_service_name,
                                                                  deployment_name,
                                                                  virtual_machine_name,
                                                                  new_network_config)
        context.request_id = result.request_id
        context.cloud_service_name = cloud_service_name
        context.virtual_machine_name = virtual_machine_name
        context.host_server_id = host_server.id
        context.trial = 0
        context.container_name = docker_container.name

        self.__clear_ports_cache()
        self.query_release_status(context)

    def query_release_status(self, context):
        vm_adapter = self.__get_azure_vm_adapter(context)
        try:
            context.trial = context.get("trial", 0) + 1
            result = vm_adapter.get_operation_status(context.request_id)
            if result.status == IN_PROGRESS and context.trial < MAX_TRIAL:
                self.log.debug('wait for release [%s] loop count [%d]' % (context.request_id, context.trial))
                self.scheduler.add_once(FEATURE, "query_release_status", context, seconds=TRIAL_INTERVAL_SECONDS)
            elif result.status == SUCCEEDED:
                context.trial = 0
                self.query_vm_status_for_release(context)
            else:
                self.log.error("timeout when configure network")
                self._on_virtual_environment_unexpected_error(context)
        except Exception as e:
            self.log.error(e)
            self.scheduler.add_once(FEATURE, "query_release_status", context, seconds=TRIAL_INTERVAL_SECONDS)

    def query_vm_status_for_release(self, context):
        vm_adapter = self.__get_azure_vm_adapter(context)
        try:
            context.trial = context.get("trial", 0) + 1
            result = vm_adapter.get_virtual_machine_instance_status(context.cloud_service_name,
                                                                    DEPLOYMENT_SLOT,
                                                                    context.virtual_machine_name)
            if result is None:
                self.log.error("cannot find vm or deployment slot")
                self._on_virtual_environment_unexpected_error(context)
            elif result == AVMStatus.READY_ROLE:
                host_server = DockerHostServer.objects(id=context.host_server_id).first()
                self.__stop_docker_container(context, host_server)
            elif context.trial > MAX_TRIAL:
                self._on_virtual_environment_unexpected_error(context)
            else:
                self.log.debug(
                    'wait for virtual machine [%r] loop count [%d]' % (context.virtual_machine_name, context.trial))
                self.scheduler.add_once(FEATURE, "query_vm_status", context, seconds=TRIAL_INTERVAL_SECONDS)
        except Exception as e:
            self.log.error(e)
            self.scheduler.add_once(FEATURE, "query_vm_status_for_release", context, seconds=TRIAL_INTERVAL_SECONDS)

    def __load_azure_key_id(self, context):
        # todo which key to use? how to support multi subscription?
        azure_key = None
        if "azure_key_id" in context:
            azure_key = AzureKey.objects(id=context.azure_key_id).first()

        if not azure_key:
            expr = Experiment.objects(id=context.experiment_id).only("azure_key").first()
            azure_key = expr.azure_key

        if not azure_key:
            hackathon = Hackathon.objects(id=context.hackathon_id).first()
            if not hackathon or (len(hackathon.azure_keys) == 0):
                raise Exception("no azure key configured")
            azure_key = hackathon.azure_keys[0]
            context.azure_key_id = azure_key.id

        return azure_key

    def __get_azure_vm_adapter(self, context):
        # todo provide a single and unified way to get adapter for hackathon
        azure_key = self.__load_azure_key_id(context)
        return VirtualMachineAdapter(azure_key.subscription_id,
                                     azure_key.get_local_pem_url(),
                                     host=azure_key.management_host)

    def __get_available_host_port(self, docker_host, private_port):
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
        containers = self.docker.list_containers(docker_host)
        used_host_ports = flatten(map(lambda p: p['Ports'], containers))

        # todo if azure return -1
        def sub(port):
            return port["PublicPort"] if "PublicPort" in port else -1

        used_public_ports = map(lambda x: sub(x), used_host_ports)
        return self.__safe_get_host_port(used_public_ports, private_port)

    def __safe_get_host_port(self, port_bindings, port):
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

    def __clear_ports_cache(self):
        """
        cache ports, if ports' number more than host_port_max_num, release the ports.
        But if there is a thread apply new ports, we will do this operation in the next loop.
        Because the host machine do not update the ports information,
        if we release ports now, the new ports will be lost.
        :return:
        """
        num = Experiment.objects(status=EStatus.STARTING).count()
        if num > 0:
            self.log.debug("there are %d experiment is starting, host ports will updated in next loop" % num)
            return
        self.log.debug("-----release ports cache successfully------")
        self.host_ports = []
