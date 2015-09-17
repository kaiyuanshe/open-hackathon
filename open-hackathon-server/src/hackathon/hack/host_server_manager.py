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
from uuid import uuid1
from time import strftime

sys.path.append("..")

from azure.servicemanagement import *
from azure.storage.blobservice import BlobService

from hackathon import Component, RequiredFeature
from hackathon.database.models import DockerHostServer, AzureKey, HackathonAzureKey

__all__ = ["DockerHostManager"]


class DockerHostManager(Component):
    """Component to manage docker host server"""
    docker = RequiredFeature("docker")

    def get_available_docker_host(self, req_count, hackathon):
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
        raise Exception("No available VM.")

    def get_host_server_by_id(self, id):
        return self.db.find_first_object_by(DockerHostServer, id=id)

    def create_docker_host_vm(self, hackathon_id):
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
        media_link = 'https://' + storage_account_name + '.blob.core.chinacloudapi.cn/' + container_name + '/' +\
                     host_name + '.vhd'
        os_hd = OSVirtualHardDisk(image_name, media_link)
        # set linux_config and endpoint_config
        customdata = self.__get_customdata_from_local_file()
        linux_config = LinuxConfigurationSet('a1', 'opentech', 'Password01!', False, custom_data=customdata)
        endpoint_config = self.__set_endpoint_config(service_name, hackathon_id)

        try:
            sms.create_virtual_machine_deployment(service_name=service_name,
                                                  network_config=endpoint_config,
                                                  deployment_name=service_name,
                                                  deployment_slot='production',
                                                  label=service_name,
                                                  role_name=service_name,
                                                  system_config=linux_config,
                                                  os_virtual_hard_disk=os_hd,
                                                  role_size='Small')
        except Exception as e:
            print ('AZURE ERROR: %s' % str(e))

    def __get_sms_object(self, hackathon_id):
        hackathon_azure_key = self.db.find_first_object_by(HackathonAzureKey, hackathon_id=hackathon_id)
        result = self.db.find_first_object_by(AzureKey, id=hackathon_azure_key.azure_key_id)
        sms = ServiceManagementService(result.subscription_id, result.pem_url, host=result.management_host)
        return sms

    def __get_available_storage_account_and_container(self, hackathon_id):
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
                                       host_base='.blob.core.chinacloudapi.cn')
            # todo host_base
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
        used_port_set = self.__get_used_public_port_set(service_name, hackathon_id)
        docker_port = 4243
        ssh_port = 9000
        while docker_port in used_port_set:
            docker_port += 1
        while ssh_port in used_port_set:
            ssh_port += 1
        assert docker_port < 40000 and ssh_port < 40000
        endpoint_config = azure.servicemanagement.ConfigurationSet()
        endpoint_config.configuration_set_type = 'NetworkConfiguration'
        endpoint1 = azure.servicemanagement.ConfigurationSetInputEndpoint(name='docker', protocol='tcp',
                                                                          port=docker_port, local_port='4243',
                                                                          load_balanced_endpoint_set_name=None,
                                                                          enable_direct_server_return=False)
        endpoint2 = azure.servicemanagement.ConfigurationSetInputEndpoint(name='SSH', protocol='tcp',
                                                                          port=ssh_port, local_port='22',
                                                                          load_balanced_endpoint_set_name=None,
                                                                          enable_direct_server_return=False)
        endpoint_config.input_endpoints.input_endpoints.append(endpoint1)
        endpoint_config.input_endpoints.input_endpoints.append(endpoint2)
        return endpoint_config

    def __deployment_exists(self, service_name, deployment_slot, hackathon_id):
        sms = self.__get_sms_object(hackathon_id)
        try:
            sms.get_deployment_by_slot(service_name, deployment_slot)
            return True
        except Exception as e:
            if e.message == 'Not found (Not Found)':
                return False
            else:
                raise Exception('Something wrong when checking deployment of service:' % service_name)

    def test(self):
        sms = self.__get_sms_object(1)

        return
