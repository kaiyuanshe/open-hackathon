# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

__author__ = 'ZGQ'

import sys
import requests
from uuid import uuid1
from time import strftime, sleep

sys.path.append("..")

from hackathon import Component, RequiredFeature, Context
from hackathon.hmongo.models import DockerHostServer, Hackathon
from hackathon.constants import (DockerPingResult, AVMStatus,
                                 DockerHostServerStatus, DHS_QUERY_STATE,
                                 ServiceDeploymentSlot, TCPProtocol,
                                 EStatus)
from hackathon.hackathon_response import ok, not_found

__all__ = ["DockerHostManager"]


class DockerHostManager(Component):
    """Component to manage docker host server"""
    docker = RequiredFeature("hosted_docker_proxy")
    expr_manager = RequiredFeature("expr_manager")

    def get_docker_hosts_list(self, hackathon):
        """
        Get all host servers of a hackathon
        :param hackathon_id: the id of this hackathon, on_success callback function
        :type hackathon_id: integer

        :return: a list of all docker hosts
        :rtype: list
        """
        host_servers = DockerHostServer.objects(hackathon=hackathon)
        return [host_server.dic() for host_server in host_servers]

    def get_available_docker_host(self, hackathon):
        vms = DockerHostServer.objects.filter(__raw__={'$where': 'this.container_count+1 < this.container_max_count'}) \
            .filter(hackathon=hackathon, state=DockerHostServerStatus.DOCKER_READY, disabled=False).all()

        if self.util.is_local():
            if len(vms) > 0:
                return Context(state=DHS_QUERY_STATE.SUCCESS, docker_host_server=vms[0])
            else:
                return Context(state=DHS_QUERY_STATE.FAILED)

        has_locked_host = False
        for host in vms:
            # check docker status
            if not self.docker.ping(host):
                host.state = DockerHostServerStatus.UNAVAILABLE
                host.save()
                continue

            # cloud service locked?
            if not self.is_host_server_locked(host):
                return Context(state=DHS_QUERY_STATE.SUCCESS, docker_host_server=host)
            else:
                has_locked_host = True

        if has_locked_host:
            # still has available host but locked
            return Context(state=DHS_QUERY_STATE.ONGOING)
        elif self.start_new_docker_host_vm(hackathon):
            # new VM is starting
            return Context(state=DHS_QUERY_STATE.ONGOING)
        else:
            # no VM found or starting
            return Context(state=DHS_QUERY_STATE.FAILED)

    def is_host_server_locked(self, docker_host):
        raise NotImplementedError()

    def get_host_server_by_id(self, id_):
        """
        Search host server in DB by id

        :param id_: the id of host server in DB
        :type id_: integer

        :return: the found host server information in DB
        :rtype: DockerHostServer object
        """
        return DockerHostServer.objects(id=id_).first()

    def schedule_pre_allocate_host_server_job(self):
        """
        Schedule pre-allocate host server for every hackathon found in DB table:hackathon
        """
        self.log.debug('Begin to check host server and prepare resource.')
        min_avavilabe_container = 5
        for hackathon in Hackathon.objects():
            if self.__exist_request_host_server_by_hackathon_id(min_avavilabe_container, hackathon.id):
                continue
            if not self.start_new_docker_host_vm(hackathon):
                self.log.error('Schedule pre-allocate host server for hackathon:%s failed.' % hackathon.name)

    def start_new_docker_host_vm(self, hackathon):
        """
        create docker host VM for hackathon whose id is hackathon_id

        :param hackathon: hackathon
        :type hackathon: Hackathon

        :return: True if send an creating VM request via API successfully after validating storage, container and
         service
         Otherwise, False
        :rtype: bool
        """
        # todo debug this logic and make sure DON'T start two or more VM at the same time
        return False

        hackathon_id = hackathon.id
        sms = self.__get_sms_object(hackathon_id)
        if sms is None:
            self.log.error('No account found for Hackathon:%d' % hackathon_id)
            return False
        # get storage and container
        res, storage_account_name, container_name = self.__get_available_storage_account_and_container(hackathon_id)
        if not res:
            return False
        # get service
        res, service_name = self.__get_available_cloud_service(hackathon_id)
        if not res:
            return False
        # set host_name to ensure its uniqueness
        host_name = str(uuid1())[0:9] + strftime("%Y%m%d%H%M%S")
        # set vm os image and hard disk storage
        image_name_default = 'b549f4301d0b4295b8e76ceb65df47d4__Ubuntu-14_04-LTS-amd64-server-20140606.1-en-us-30GB'
        image_name = self.util.safe_get_config('dockerhostserver.vm.image_name', image_name_default)
        media_link = 'https://%s.blob.core.chinacloudapi.cn/%s/%s.vhd' % (storage_account_name, container_name,
                                                                          host_name)
        os_hd = OSVirtualHardDisk(image_name, media_link)
        # set linux_config and endpoint_config
        customdata = self.__get_customdata_from_local_file()
        linux_config = LinuxConfigurationSet(host_name,
                                             self.util.safe_get_config('dockerhostserver.vm.username', 'opentech'),
                                             self.util.safe_get_config('dockerhostserver.vm.password', 'Password01!'),
                                             False, custom_data=customdata)
        endpoint_config = self.__set_endpoint_config(service_name, hackathon_id)
        deployment_exist = True
        deployment_slot = ServiceDeploymentSlot.PRODUCTION
        try:
            deployment_exist = self.__deployment_exists(service_name, deployment_slot, hackathon_id)
        except Exception as e:
            self.log.error(e)
            return False
        if not deployment_exist:
            try:
                result = sms.create_virtual_machine_deployment(service_name=service_name,
                                                               network_config=endpoint_config,
                                                               deployment_name=service_name,
                                                               deployment_slot=deployment_slot,
                                                               label=service_name,
                                                               role_name=host_name,
                                                               system_config=linux_config,
                                                               os_virtual_hard_disk=os_hd,
                                                               role_size=0)
                self.log.debug('To create VM:%s in service:%s.(deployment)' % (host_name, service_name))
            except Exception as e:
                self.log.error(e)
                return False
        else:
            try:
                result = sms.add_role(service_name=service_name,
                                      deployment_name=service_name,
                                      role_name=host_name,
                                      system_config=linux_config,
                                      os_virtual_hard_disk=os_hd,
                                      network_config=endpoint_config,
                                      role_size=0)
                self.log.debug('To create VM:%s in service:%s.(add role)' % (host_name, service_name))
            except Exception as e:
                self.log.error(e)
                return False
        # storage parameters in context
        context = Context(hackathon_id=hackathon_id, request_id=result.request_id,
                          service_name=service_name, role_name=host_name,
                          deployment_name=service_name, deployment_slot=deployment_slot,
                          host_name=host_name)
        # start schedule
        self.sche.add_once('docker_host_manager', 'check_vm_status', context=context, minutes=5)
        return True

    def add_host_server(self, hackathon, args):
        """
        create a docker host DB object for a hackathon and insert record into the database.
        param-"args" contain all necessary infos to new a docker_host

        :return: return True if succeed, otherwise return False
        :rtype: bool
        """

        host_server = DockerHostServer(vm_name=args.vm_name,
                                       public_dns=args.public_dns,
                                       public_ip=args.public_ip,
                                       public_docker_api_port=args.public_docker_api_port,
                                       private_ip=args.private_ip,
                                       private_docker_api_port=args.private_docker_api_port,
                                       container_count=0,
                                       container_max_count=args.container_max_count,
                                       is_auto=False,
                                       disabled=args.get("disabled", False),
                                       hackathon=hackathon)

        if self.docker.ping(host_server):
            host_server.state = DockerHostServerStatus.DOCKER_READY
        else:
            host_server.state = DockerHostServerStatus.UNAVAILABLE

        host_server.save()
        return host_server.dic()

    def get_and_check_host_server(self, host_server_id):
        """
        first get the docker host DB object for a hackathon,
        and check whether the container_count is correct through "Docker Restful API",
        if not, update this value in the database.

        :param host_server_id: the id of host_server in DB
        :type host_server_id: Integer

        :return: A object of docker_host_server
        :rtype: DockerHostServer object or None
        """
        host_server = DockerHostServer.objects(id=host_server_id).first()
        if host_server is None:
            self.log.warn('get docker_host fail, not find host server by id:' + host_server_id)
            return not_found("docker host server not found")

        ping = self.docker.ping(host_server)
        if not ping:
            host_server.state = DockerHostServerStatus.UNAVAILABLE
            host_server.save()
        else:
            try:
                containers = self.docker.list_containers(host_server)
                if len(containers) != host_server.container_count:
                    host_server.container_count = len(containers)
                    host_server.save()
            except Exception as e:
                self.log.error("Failed in sync container count")
                self.log.error(e)

        return self.__check_docker_host_server(host_server).dic()

    def __check_docker_host_server(self, host_server):
        ping = self.docker.ping(host_server)
        if not ping:
            host_server.state = DockerHostServerStatus.UNAVAILABLE
            host_server.save()
        else:
            try:
                containers = self.docker.list_containers(host_server)
                if len(containers) != host_server.container_count:
                    host_server.container_count = len(containers)
                    host_server.save()
            except Exception as e:
                self.log.error("Failed in sync container count")
                self.log.error(e)

        return host_server

    def update_host_server(self, args):
        """
        update a docker host_server's information for a hackathon.

        :param hackathon_id: the id of hackathon in DB
        :type hackathon_id: Integer

        :return: ok() if succeed.
                 not_found(...) if fail to update the docker_host's information
        """
        vm = DockerHostServer.objects(id=args.id).first()
        if vm is None:
            self.log.warn('delete docker_host fail, not find hostserver_id:' + args.id)
            return not_found("", "host_server not found")

        vm.vm_name = args.get("vm_name", vm.vm_name)
        vm.public_dns = args.get("public_dns", vm.public_dns)
        vm.public_ip = args.get("public_ip", vm.public_ip)
        vm.private_ip = args.get("private_ip", vm.private_ip)
        vm.container_max_count = int(args.get("container_max_count", vm.container_max_count))
        vm.public_docker_api_port = int(args.get("public_docker_api_port", vm.public_docker_api_port))
        vm.private_docker_api_port = int(args.get("private_docker_api_port", vm.private_docker_api_port))
        vm.disabled = args.get("disabled", vm.disabled)
        if self.docker.ping(vm):
            vm.state = DockerHostServerStatus.DOCKER_READY
        else:
            vm.state = DockerHostServerStatus.UNAVAILABLE

        vm.save()
        return self.__check_docker_host_server(vm).dic()

    def delete_host_server(self, host_server_id):
        """
        delete a docker host_server for a hackathon.

        :param host_server_id: the id of host_server in DB
        :type host_server_id: Integer

        :return: ok() if succeeds or this host_server doesn't exist
                 precondition_failed() if there are still some containers running
        """
        DockerHostServer.objects(id=host_server_id).delete()
        return ok()

    def check_vm_status(self, context):
        raise NotImplementedError()

    def get_hostserver_info(self, host_server_id):
        """
        Get the infomation of a hostserver by host_server_id

        :type host_server_id: int
        :param host_server_id: the id of host_server

        :rtype: dict
        :return: the dict of host_server detail information
        """
        host_server = self.db.find_first_object_by(DockerHostServer, id=host_server_id)
        return host_server.dic()

    def check_subscription_id(self, hackathon_id):
        try:
            sms = self.__get_sms_object(hackathon_id)
            sms.list_hosted_services()
        except Exception:
            return False

        return True

    def __get_sms_object(self, hackathon_id):
        raise NotImplementedError()

    def __get_available_storage_account_and_container(self, hackathon_id):
        raise NotImplementedError()

    def __get_available_cloud_service(self, hackathon_id):
        raise NotImplementedError()

    def __get_customdata_from_local_file(self):
        """
        Get customdata from local file

        :return: content of file if successfully read, otherwise return None and VM will not do customization work.
        :rtype: str|unicode
        """
        sh_file = []
        file_path = self.util.safe_get_config('dockerhostserver.vm.customdata',
                                              'open-hackathon-server/customdata.sh')
        try:
            for line in open(file_path):
                sh_file.append(line)
            customdata = '\r\n'.join(sh_file)
            return customdata
        except Exception as e:
            self.log.error('Encounter an error when reading customdata from local file')
            self.log.error(e)
        return None

    def __get_used_public_port_set(self, service_name, hackathon_id):
        raise NotImplementedError()
    def __set_endpoint_config(self, service_name, hackathon_id):
        raise NotImplementedError()

    def __deployment_exists(self, service_name, deployment_slot, hackathon_id):
        raise NotImplementedError()

    def __exist_request_host_server_by_hackathon_id(self, request_count, hackathon_id):
        """
        check whether there is a host server, belonging to a hackathon, that can hold a few more containers

        :param request_count: the number of containers needed
        :type request_count: integer

        :param hackathon_id: the id of hackathon
        :type hackathon_id: integer

        :return: True if there exists one host server at least, otherwise False
        :rtype: bool
        """
        vms = self.db.find_all_objects(DockerHostServer,
                                       DockerHostServer.container_count + request_count <=
                                       DockerHostServer.container_max_count,
                                       DockerHostServer.hackathon_id == hackathon_id,
                                       DockerHostServer.state == DockerHostServerStatus.DOCKER_READY,
                                       DockerHostServer.disabled == DockerHostServerDisable.ABLE)
        return len(vms) > 0
