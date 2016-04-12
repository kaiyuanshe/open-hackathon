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
from hackathon.hazure.cloud_service_adapter import CloudServiceAdapter

__author__ = 'ZGQ'

import sys
import requests
from uuid import uuid1
from time import strftime, sleep

sys.path.append("..")

from azure.storage.blob import BlobService
from azure.servicemanagement import (ConfigurationSet, ConfigurationSetInputEndpoint, OSVirtualHardDisk,
                                     LinuxConfigurationSet, ServiceManagementService)

from hackathon import Component, RequiredFeature, Context
from hackathon.hmongo.models import DockerHostServer, Hackathon
from hackathon.constants import (AzureApiExceptionMessage, DockerPingResult, AVMStatus, AzureVMPowerState,
                                 DockerHostServerStatus, DHS_QUERY_STATE,
                                 ServiceDeploymentSlot, AzureVMSize, AzureVMEndpointName, TCPProtocol,
                                 AzureVMEndpointDefaultPort, AzureVMEnpointConfigType, AzureOperationStatus, EStatus)
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
        # todo which azure key to use?
        azure_key = docker_host.hackathon.azure_keys[0]
        cloudservice = CloudServiceAdapter(azure_key.subscription_id,
                                           azure_key.get_local_pem_url(),
                                           host=azure_key.management_host)
        service_name = docker_host.public_dns.split(".")[0]
        return cloudservice.is_cloud_service_locked(service_name)

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
        for hackathon in self.db.find_all_objects(Hackathon):
            if self.__exist_request_host_server_by_hackathon_id(min_avavilabe_container, hackathon.id):
                continue
            if not self.start_new_docker_host_vm(hackathon):
                self.log.error('Schedule pre-allocate host server for hackathon:%s failed.' % hackathon.name)

    def start_new_docker_host_vm(self, hackathon):
        """
        create docker host VM for hackathon whose id is hackathon_id

        :param hackathon: hackathon
        :type hackathon: Hackathon

        :return: True if send an Azure creating VM request via API successfully after validating storage, container and
         service
         Otherwise, False
        :rtype: bool
        """
        # todo debug this logic and make sure DON'T start two or more VM at the same time
        return False

        hackathon_id = hackathon.id
        sms = self.__get_sms_object(hackathon_id)
        if sms is None:
            self.log.error('No Azure account found for Hackathon:%d' % hackathon_id)
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
                                                               role_size=AzureVMSize.MEDIUM_SIZE)
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
                                      role_size=AzureVMSize.MEDIUM_SIZE)
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
        """
        Check vm status, including Azure creation operation feedback and docker api port
        and then add it to DB

        :param context: must has key:
                        "hackathon_id": value type is integer, the id of hackathon;
                        "request_id": value type is str|unicode, the id of Azure operation;
                        "service_name": value type is str|unicode, the name of cloud service;
                        "role_name": value type is str|unicode, the name of VM role;
                        "deployment_name": value type is str|unicode, the name of service deployment;
                        "deployment_slot": value type is str|unicode, the slot of service deployment;
                        "host_name": value type is str|unicode, the name of VM host
        :type context: Context

        """
        assert context.get('hackathon_id') and context.get('request_id') and context.get('service_name')
        assert context.get('role_name') and context.get('deployment_name') and context.get('deployment_slot')
        assert context.get('host_name')
        sms = self.__get_sms_object(context.hackathon_id)
        if sms is None:
            self.log.error('Something wrong with Azure account of Hackathon:%d' % context.hackathon_id)
            return
        # check Azure vm creation operation status
        result = sms.get_operation_status(context.request_id)
        try:
            while result.status == AzureOperationStatus.IN_PROGRESS:
                sleep(5)
                result = sms.get_operation_status(context.request_id)
            if result.status != AzureOperationStatus.SUCCESS:
                self.log.error('VM creation operation failed according to Azure response.')
                return
        except Exception as e:
            self.log.error(e)
            return
        # get network config
        public_dns = ''
        private_ip = ''
        public_ip = ''
        public_docker_api_port = 0
        private_docker_api_port = 0
        state = DockerHostServerStatus.STARTING
        try:
            properties = sms.get_hosted_service_properties(context.service_name, True)
            for deployment in properties.deployments.deployments:
                if deployment.name.lower() == context.deployment_name.lower() \
                        and deployment.deployment_slot.lower() == context.deployment_slot.lower():
                    public_dns = deployment.url[7:-1]
                    for role in deployment.role_instance_list.role_instances:
                        if role.role_name == context.role_name:
                            if role.instance_status.lower() == AVMStatus.READY_ROLE.lower() \
                                    and role.power_state.lower() == AzureVMPowerState.VM_STARTED.lower():
                                state = DockerHostServerStatus.DOCKER_INIT
                            else:
                                state = DockerHostServerStatus.UNAVAILABLE
                            private_ip = role.ip_address
                            for endpoint in role.instance_endpoints:
                                if endpoint.name.lower() == AzureVMEndpointName.DOCKER.lower():
                                    private_docker_api_port = int(endpoint.local_port)
                                    public_docker_api_port = int(endpoint.public_port)
                                    public_ip = endpoint.vip
        except Exception as e:
            self.log.error(e)
            return
        # add this VM to db
        self.log.debug(public_dns)
        db_object = self.db.add_object_kwargs(DockerHostServer, vm_name=context.host_name, public_dns=public_dns,
                                              public_ip=public_ip, public_docker_api_port=public_docker_api_port,
                                              private_ip=private_ip, private_docker_api_port=private_docker_api_port,
                                              container_count=0, is_auto=True, state=state,
                                              disable=False,
                                              container_max_count=self.util.safe_get_config(
                                                  'dockerhostserver.vm.container_max_count', 50),
                                              hackathon_id=context.hackathon_id)
        self.db.commit()
        # check docker _ping port
        try:
            ping_url = 'http://%s:%d/_ping' % (public_ip, public_docker_api_port)
            req = requests.get(ping_url)
            self.log.debug(req.content)
            if req.status_code == 200 and req.content == DockerPingResult.OK:
                self.db.update_object(db_object, state=DockerHostServerStatus.DOCKER_READY)
                self.db.commit()
        except Exception as e:
            self.log.error(e)

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
        """
        Get ServiceManagementService object by Azure account which is related to hackathon_id

        :param hackathon_id: the id of hackathon
        :type hackathon_id: integer

        :return: ServiceManagementService object
        :rtype: class 'azure.servicemanagement.servicemanagementservice.ServiceManagementService'
        """
        hackathon_azure_key = self.db.find_first_object_by(HackathonAzureKey, hackathon_id=hackathon_id)

        if hackathon_azure_key is None:
            self.log.error('Found no azure key with Hackathon:%d' % hackathon_id)
            return None

        sms = ServiceManagementService(hackathon_azure_key.azure_key.subscription_id,
                                       hackathon_azure_key.azure_key.get_local_pem_url(),
                                       host=hackathon_azure_key.azure_key.management_host)
        return sms

    def __get_available_storage_account_and_container(self, hackathon_id):
        """
        Get available storage account and container

        :param hackathon_id: the id of hackathon
        :type hackathon_id: integer

        :return: if there is available storage account and container, then return (True, storage
                 account name, container name). Otherwise, return (False, None, None)
        :rtype: 3-element tuple: (bool, str|unicode, str|unicode)
        """
        container_name = self.util.safe_get_config('dockerhostserver.azure.container', 'dockerhostprivatecontainer')
        sms = self.__get_sms_object(hackathon_id)
        if sms is None:
            self.log.error('Something wrong with Azure account of Hackathon:%d' % hackathon_id)
            return False, None, None
        storage_accounts = sms.list_storage_accounts()
        # check storage account one by one, return True once find a qualified one
        for storage in storage_accounts.storage_services:
            try:
                storage_response = sms.get_storage_account_keys(storage.service_name)
            except Exception as e:
                self.log.error('Encounter an error when checking storage_account:%s ' % storage.service_name)
                self.log.error(e)
                continue
            blob_service = BlobService(account_name=storage.service_name,
                                       account_key=storage_response.storage_service_keys.primary,
                                       host_base=self.util.safe_get_config('dockerhostserver.storage.host_base',
                                                                           '.blob.core.chinacloudapi.cn'))
            try:
                blob_service.get_container_metadata(container_name)
                return True, storage.service_name, container_name
            except Exception as e:
                if e.message != AzureApiExceptionMessage.CONTAINER_NOT_FOUND:
                    self.log.error('Encounter an error when checking container:%s ' % container_name)
                    self.log.error(e)
                    continue
            try:
                blob_service.create_container(container_name=container_name, x_ms_blob_public_access='container')
                return True, storage.service_name, container_name
            except Exception as e:
                self.log.error('Encounter an error when creating container:%s ' % container_name)
                self.log.error(e)
        return False, None, None

    def __get_available_cloud_service(self, hackathon_id):
        """
        Get available cloud service

        :param hackathon_id: the id of hackathon
        :type hackathon_id: integer

        :return: if there is a available cloud service, then return (True, cloud service name). Otherwise, return
                (False, None).
        :rtype: 2-element tuple: (bool, str|unicode)
        """
        config_name = self.util.safe_get_config('dockerhostserver.azure.cloud_service.name',
                                                'dockerhostprivatecloudservice')
        service_name = config_name + str(hackathon_id)
        service_location = self.util.safe_get_config('dockerhostserver.azure.cloud_service.location', 'China East')
        sms = self.__get_sms_object(hackathon_id)
        if sms is None:
            self.log.error('Something wrong with Azure account of Hackathon:%d' % hackathon_id)
            return False, None
        try:
            sms.get_hosted_service_properties(service_name, True)
            return True, service_name
        except Exception as e:
            if e.message != AzureApiExceptionMessage.SERVICE_NOT_FOUND:
                self.log.error('Encounter an error when checking cloud service:%s ' % service_name)
                self.log.error(e)
                return False, None
        # not found, then create one
        try:
            if sms.check_hosted_service_name_availability(service_name=service_name).result:
                sms.create_hosted_service(service_name=service_name, label=service_name, location=service_location)
                return True, service_name
            else:
                self.log.error('Cloud service name:%s is not available. ' % service_name)
                return False, None
        except Exception as e:
            self.log.error('Encounter an error when creating cloud service:%s ' % service_name)
            self.log.error(e)
        return False, None

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
        """
        Get the set of used public ports of cloud service in Azure account which is related to hackathon_id

        :param service_name: the name of cloud service
        :type service_name: str|unicode

        :param hackathon_id: the id of hackathon
        :type hackathon_id: integer

        :return: the set of used public ports
        :rtype: a list of integer
        """
        sms = self.__get_sms_object(hackathon_id)
        if sms is None:
            self.log.error('Something wrong with Azure account of Hackathon:%d' % hackathon_id)
            raise Exception('Something wrong with Azure account of Hackathon:%d' % hackathon_id)
        endpoints = []
        properties = sms.get_hosted_service_properties(service_name, True)
        for deployment in properties.deployments.deployments:
            for role in deployment.role_list.roles:
                for configuration_set in role.configuration_sets.configuration_sets:
                    if configuration_set.configuration_set_type == AzureVMEnpointConfigType.NETWORK:
                        if configuration_set.input_endpoints is not None:
                            for input_endpoint in configuration_set.input_endpoints.input_endpoints:
                                endpoints.append(input_endpoint.port)
        return map(lambda x: int(x), endpoints)

    def __set_endpoint_config(self, service_name, hackathon_id):
        """
        Set endpoint configuration which is need in creating Azure VM

        :param service_name: the name of cloud service
        :type service_name: str|unicode

        :param hackathon_id: the id of hackathon
        :type hackathon_id: integer

        :return: the endpoint configuration set
        :rtype: class 'azure.servicemanagement.ConfigurationSet'
        """
        used_port_set = self.__get_used_public_port_set(service_name, hackathon_id)
        docker_port = 4243
        ssh_port = 9000
        while docker_port in used_port_set:
            docker_port += 1
        while ssh_port in used_port_set:
            ssh_port += 1
        assert docker_port < 40000 and ssh_port < 40000
        endpoint_config = ConfigurationSet()
        endpoint_config.configuration_set_type = AzureVMEnpointConfigType.NETWORK
        endpoint1 = ConfigurationSetInputEndpoint(name=AzureVMEndpointName.DOCKER, protocol=TCPProtocol.TCP,
                                                  port=str(docker_port),
                                                  local_port=str(AzureVMEndpointDefaultPort.DOCKER),
                                                  load_balanced_endpoint_set_name=None,
                                                  enable_direct_server_return=False)
        endpoint2 = ConfigurationSetInputEndpoint(name=AzureVMEndpointName.SSH, protocol=TCPProtocol.TCP,
                                                  port=str(ssh_port),
                                                  local_port=str(AzureVMEndpointDefaultPort.SSH),
                                                  load_balanced_endpoint_set_name=None,
                                                  enable_direct_server_return=False)
        endpoint_config.input_endpoints.input_endpoints.append(endpoint1)
        endpoint_config.input_endpoints.input_endpoints.append(endpoint2)
        return endpoint_config

    def __deployment_exists(self, service_name, deployment_slot, hackathon_id):
        """
        Check whether the deployment of a cloud service exists in the Azure account which is related to hackathon_id

        :param service_name:the name of service
        :type service_name: str|unicode

        :param deployment_slot: the slot of deployment
        :type deployment_slot: str|unicode

        :param hackathon_id: the id of hackathon
        :type hackathon_id: integer

        :return: True if there does exist the cloud service
                 False if not found such a service
        :rtype: bool

        :raise: raise exception when something went wrong with Azure api
                "Something wrong with checking deployment of service:service_name"
        :type: Exception
        """
        sms = self.__get_sms_object(hackathon_id)
        if sms is None:
            self.log.error('Something wrong with Azure account of Hackathon:%d' % hackathon_id)
            raise Exception('Something wrong with Azure account of Hackathon:%d' % hackathon_id)
        try:
            sms.get_deployment_by_slot(service_name, deployment_slot)
            return True
        except Exception as e:
            if e.message == AzureApiExceptionMessage.DEPLOYMENT_NOT_FOUND:
                return False
            else:
                raise Exception('Something wrong with checking deployment of service:' % service_name)

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
