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
import requests
from uuid import uuid1
from time import strftime, sleep

sys.path.append("..")

from azure.servicemanagement import *
from azure.storage.blobservice import BlobService
from azure.servicemanagement import ConfigurationSet, ConfigurationSetInputEndpoint

from hackathon import Component, RequiredFeature, Context
from hackathon.database.models import DockerHostServer, AzureKey, HackathonAzureKey, Hackathon

__all__ = ["DockerHostManager"]


class DockerHostManager(Component):
    """Component to manage docker host server"""
    docker = RequiredFeature("docker")
    sche = RequiredFeature("scheduler")

    def get_available_docker_host(self, req_count, hackathon):
        """
        Get available docker host from DB
        If there is no qualified host, then create one

        :param req_count: the number of containers needed
        :type req_count: integer

        :param hackathon: a record in DB table:hackathon
        :type hackathon: Hackathon object

        :return: a docker host if there is a qualified one, otherwise None
        :rtype: DockerHostServer object
        """
        vms = self.db.find_all_objects(DockerHostServer,
                                       DockerHostServer.container_count + req_count <=
                                       DockerHostServer.container_max_count,
                                       DockerHostServer.hackathon_id == hackathon.id)
        # todo connect to azure to launch new VM if no existed VM meet the requirement
        # since it takes some time to launch VM,
        # it's more reasonable to launch VM when the existed ones are almost used up.
        # The new-created VM must run 'cloudvm service by default(either cloud-init or python remote ssh)
        # todo the VM public/private IP will change after reboot, need sync the IP in db with azure in this case
        for docker_host in vms:
            if self.docker.hosted_docker.ping(docker_host):
                return docker_host
        self.create_docker_host_vm(hackathon.id)
        return None
        # raise Exception("No available VM.")

    def get_host_server_by_id(self, id):
        """
        Search host server in DB by id

        :param id: the id of host server in DB
        :type id: integer

        :return: the found host server information in DB
        :rtype: DockerHostServer object
        """
        return self.db.find_first_object_by(DockerHostServer, id=id)

    def schedule_pre_allocate_host_server_job(self):
        """
        Schedule pre-allocate host server for every hackathon found in DB table:hackathon
        """
        self.log.debug('Begin to check host server and prepare resource.')
        min_avavilabe_container = 5
        for hackathon in self.db.find_all_objects(Hackathon):
            if self.__exist_request_host_server_by_hackathon_id(min_avavilabe_container, hackathon.id):
                continue
            if not self.create_docker_host_vm(hackathon.id):
                self.log.error('Schedule pre-allocate host server for hackathon:%s failed.' % hackathon.display_name)

    def create_docker_host_vm(self, hackathon_id):
        """
        create docker host VM for hackathon whose id is hackathon_id

        :param hackathon_id: the id of hackathon in DB table:hackathon
        :type hackathon_id: Integer

        :return: True if send an Azure creating VM request via API successfully after validating storage, container and
         service
         Otherwise, False
        :rtype: bool
        """
        sms = self.__get_sms_object(hackathon_id)
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
        deployment_slot = 'production'
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
                                                               role_size='Medium')
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
                                      role_size='Medium')
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
        # check Azure vm creation operation status
        result = sms.get_operation_status(context.request_id)
        try:
            while result.status == 'InProgress':
                sleep(5)
                result = sms.get_operation_status(context.request_id)
            if result.status != 'Succeeded':
                self.log.error('VM creation operation failed when...')
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
        state = 0
        try:
            properties = sms.get_hosted_service_properties(context.service_name, True)
            for deployment in properties.deployments.deployments:
                if deployment.name.lower() == context.deployment_name.lower() \
                        and deployment.deployment_slot.lower() == context.deployment_slot.lower():
                    public_dns = deployment.url[7:-1]
                    for role in deployment.role_instance_list.role_instances:
                        if role.role_name == context.role_name:
                            if role.instance_status.lower() == 'readyrole' \
                                    and role.power_state.lower() == 'started':
                                state = 1
                            else:
                                state = 3
                            private_ip = role.ip_address
                            for endpoint in role.instance_endpoints:
                                if endpoint.name.lower() == 'docker':
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
                                              container_count=0, is_auto=1, state=state, disable=0,
                                              container_max_count=self.util.safe_get_config(
                                                  'dockerhostserver.vm.container_max_count', 50),
                                              hackathon_id=context.hackathon_id)
        self.db.commit()
        # check docker _ping port
        try:
            ping_url = 'http://%s:%d/_ping' % (public_dns, public_docker_api_port)
            req = requests.get(ping_url)
            self.log.debug(req.content)
            if req.status_code == 200 and req.content == 'OK':
                self.db.update_object(db_object, state=2)
                self.db.commit()
        except Exception as e:
            self.log.error(e)

    def __get_sms_object(self, hackathon_id):
        """
        Get ServiceManagementService object by Azure account which is related to hackathon_id

        :param hackathon_id: the id of hackathon
        :type hackathon_id: integer

        :return: ServiceManagementService object
        :rtype: class 'azure.servicemanagement.servicemanagementservice.ServiceManagementService'
        """
        hackathon_azure_key = self.db.find_first_object_by(HackathonAzureKey, hackathon_id=hackathon_id)
        result = self.db.find_first_object_by(AzureKey, id=hackathon_azure_key.azure_key_id)
        sms = ServiceManagementService(result.subscription_id, result.pem_url, host=result.management_host)
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
                if e.message != 'Not found (The specified container does not exist.)':
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
        try:
            sms.get_hosted_service_properties(service_name, True)
            return True, service_name
        except Exception as e:
            if e.message != 'Not found (Not Found)':
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

        :return: content of file if successfully read, otherwise return None
        :rtype: str|unicode
        """
        sh_file = []
        file_path = self.util.safe_get_config('dockerhostserver.vm.customdata', '/home/guiquan/Desktop/test2.sh')
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
        endpoints = []
        properties = sms.get_hosted_service_properties(service_name, True)
        for deployment in properties.deployments.deployments:
            for role in deployment.role_list.roles:
                for configuration_set in role.configuration_sets.configuration_sets:
                    if configuration_set.configuration_set_type == 'NetworkConfiguration':
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
        endpoint_config.configuration_set_type = 'NetworkConfiguration'
        endpoint1 = ConfigurationSetInputEndpoint(name='docker', protocol='tcp',
                                                  port=docker_port, local_port='4243',
                                                  load_balanced_endpoint_set_name=None,
                                                  enable_direct_server_return=False)
        endpoint2 = ConfigurationSetInputEndpoint(name='SSH', protocol='tcp',
                                                  port=ssh_port, local_port='22',
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
        try:
            sms.get_deployment_by_slot(service_name, deployment_slot)
            return True
        except Exception as e:
            if e.message == 'Not found (Not Found)':
                return False
            else:
                raise Exception('Something wrong with checking deployment of service:' % service_name)

    def __find_all_hackathon_id(self):
        """
        Get all ids of hackathon from DB table:hackathon

        :return: the set of all hackathon ids
        :rtype: the list of integer
        """
        hackathon_ids = []
        hackathon_objects = self.db.find_all_objects(Hackathon)
        for hackathon in hackathon_objects:
            hackathon_ids.append(hackathon.id)
        return hackathon_ids

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
                                       DockerHostServer.state == 2,
                                       DockerHostServer.disable == 0)
        return len(vms) > 0


