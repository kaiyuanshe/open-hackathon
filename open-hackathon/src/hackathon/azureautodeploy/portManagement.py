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

__author__ = 'Yifu Huang'

import sys

sys.path.append("..")
from hackathon.azureautodeploy.azureUtil import *
from azure.servicemanagement import *
import time


class PortManagement():
    def __init__(self):
        self.sms = None

    def connect(self, subscription_id, pem_url, management_host):
        """
        Connect to azure service management service
        :param subscription_id:
        :param pem_url:
        :param management_host:
        :return:
        """
        try:
            self.sms = ServiceManagementService(subscription_id, pem_url, management_host)
        except Exception as e:
            log.error(e)
            return False
        return True

    def assign_public_port(self, cloud_service_name, deployment_slot, virtual_machine_name, private_ports):
        """
        Assign public port of cloud service for private port of virtual machine
        Return -1 if failed
        :param cloud_service_name:
        :param deployment_slot:
        :param virtual_machine_name:
        :param private_port:
        :return:
        """
        assigned_ports = self.__get_assigned_ports(cloud_service_name)
        if assigned_ports is None:
            return -1
        # duplicate detection for public port
        public_ports = []
        for p in private_ports:
            public_port = int(p)
            while str(public_port) in assigned_ports or str(public_port) in public_ports:
                public_port = (public_port + 1) % 65536
            public_ports.append(public_port)
        # compose network config to update
        try:
            deployment = self.sms.get_deployment_by_slot(cloud_service_name, deployment_slot)
        except Exception as e:
            log.error(e)
            return -1
        network = self.__compose_network_config(cloud_service_name,
                                                deployment.name,
                                                virtual_machine_name,
                                                public_ports,
                                                private_ports)
        if network is None:
            return -1
        try:
            result = self.sms.update_role(cloud_service_name,
                                          deployment.name,
                                          virtual_machine_name,
                                          network_config=network)
        except Exception as e:
            log.error(e)
            return -1
        if not self.__wait_for_async(result.request_id, 5, 200):
            log.error(WAIT_FOR_ASYNC + ' ' + FAIL)
            return -1
        if not self.__wait_for_role(cloud_service_name,
                                    deployment.name,
                                    virtual_machine_name,
                                    5,
                                    200):
            log.error('%s %s not ready' % (VIRTUAL_MACHINE, virtual_machine_name))
            return -1
        return [int(p) for p in public_ports]

    def release_public_port(self, cloud_service_name, deployment_slot, virtual_machine_name, private_ports):
        """
        Release public port of cloud service according to private port of virtual machine
        Return False if failed
        :param cloud_service_name:
        :param deployment_slot:
        :param virtual_machine_name:
        :param private_port:
        :return:
        """
        # decompose network config to update
        try:
            deployment = self.sms.get_deployment_by_slot(cloud_service_name, deployment_slot)
        except Exception as e:
            log.error(e)
            return False
        network = self.__decompose_network_config(cloud_service_name,
                                                  deployment.name,
                                                  virtual_machine_name,
                                                  private_ports)
        if network is None:
            return False
        try:
            result = self.sms.update_role(cloud_service_name,
                                          deployment.name,
                                          virtual_machine_name,
                                          network_config=network)
        except Exception as e:
            log.error(e)
            return False
        if not self.__wait_for_async(result.request_id, 5, 200):
            log.error(WAIT_FOR_ASYNC + ' ' + FAIL)
            return False
        if not self.__wait_for_role(cloud_service_name,
                                    deployment.name,
                                    virtual_machine_name,
                                    5,
                                    200):
            log.error('%s %s not ready' % (VIRTUAL_MACHINE, virtual_machine_name))
            return False
        return True

    # ---------------------------------------- helper functions ---------------------------------------- #

    def __get_assigned_ports(self, cloud_service_name):
        """
        Get the list of assigned ports of specific cloud service
        Return None if failed
        :param cloud_service_name:
        :return:
        """
        try:
            properties = self.sms.get_hosted_service_properties(cloud_service_name, True)
        except Exception as e:
            log.error(e)
            return None
        ports = []
        for deployment in properties.deployments.deployments:
            for role in deployment.role_list.roles:
                for configuration_set in role.configuration_sets.configuration_sets:
                    if configuration_set.configuration_set_type == 'NetworkConfiguration':
                        if configuration_set.input_endpoints is not None:
                            for input_endpoint in configuration_set.input_endpoints.input_endpoints:
                                ports.append(input_endpoint.port)
        return ports

    def __compose_network_config(self, cloud_service_name, deployment_name,
                                 virtual_machine_name, public_port, private_port):
        """
        Create a new network config by adding given endpoint
        Return None if failed
        :param cloud_service_name:
        :param deployment_name:
        :param virtual_machine_name:
        :param public_port:
        :param private_port:
        :return:
        """
        try:
            virtual_machine = self.sms.get_role(cloud_service_name, deployment_name, virtual_machine_name)
        except Exception as e:
            log.error(e)
            return None
        network = ConfigurationSet()
        network.configuration_set_type = 'NetworkConfiguration'
        for configuration_set in virtual_machine.configuration_sets.configuration_sets:
            if configuration_set.configuration_set_type == 'NetworkConfiguration':
                if configuration_set.input_endpoints is not None:
                    for input_endpoint in configuration_set.input_endpoints.input_endpoints:
                        network.input_endpoints.input_endpoints.append(
                            ConfigurationSetInputEndpoint(input_endpoint.name,
                                                          input_endpoint.protocol,
                                                          input_endpoint.port,
                                                          input_endpoint.local_port)
                        )
                    break
        for i in range(len(public_port)):
            network.input_endpoints.input_endpoints.append(
                ConfigurationSetInputEndpoint('auto-' + str(public_port[i]), 'tcp', str(public_port[i]),
                                              str(private_port[i]))
            )
        return network

    def __decompose_network_config(self, cloud_service_name, deployment_name, virtual_machine_name, private_ports):
        """
        Create a new network config by deleting given endpoint
        Return None if failed
        :param cloud_service_name:
        :param deployment_name:
        :param virtual_machine_name:
        :param private_ports:
        :return:
        """
        try:
            virtual_machine = self.sms.get_role(cloud_service_name, deployment_name, virtual_machine_name)
        except Exception as e:
            log.error(e)
            return None
        private_endpoints = map(str, private_ports)
        network = ConfigurationSet()
        network.configuration_set_type = 'NetworkConfiguration'
        for configuration_set in virtual_machine.configuration_sets.configuration_sets:
            if configuration_set.configuration_set_type == 'NetworkConfiguration':
                if configuration_set.input_endpoints is not None:
                    for input_endpoint in configuration_set.input_endpoints.input_endpoints:
                        if input_endpoint.local_port not in private_endpoints:
                            network.input_endpoints.input_endpoints.append(
                                ConfigurationSetInputEndpoint(input_endpoint.name,
                                                              input_endpoint.protocol,
                                                              input_endpoint.port,
                                                              input_endpoint.local_port)
                            )
        return network

    def __wait_for_async(self, request_id, second_per_loop, loop):
        count = 0
        result = self.sms.get_operation_status(request_id)
        while result.status == 'InProgress':
            log.debug('%s [%s] loop count [%d]' % ('wait for async', request_id, count))
            count += 1
            if count > loop:
                log.error('Timed out waiting for async operation to complete.')
                return False
            time.sleep(second_per_loop)
            result = self.sms.get_operation_status(request_id)
        if result.status != 'Succeeded':
            log.error(vars(result))
            if result.error:
                log.error(result.error.code)
                log.error(vars(result.error))
            log.error('Asynchronous operation did not succeed.')
            return False
        return True

    def __wait_for_role(self, service_name, deployment_name, role_instance_name,
                        second_per_loop, loop, status='ReadyRole'):
        count = 0
        props = self.sms.get_deployment_by_name(service_name, deployment_name)
        while self.__get_role_instance_status(props, role_instance_name) != status:
            log.debug('_wait_for_role [%s] loop count: %d' % (role_instance_name, count))
            count += 1
            if count > loop:
                log.error('Timed out waiting for role instance status.')
                return False
            time.sleep(second_per_loop)
            props = self.sms.get_deployment_by_name(service_name, deployment_name)
        return self.__get_role_instance_status(props, role_instance_name) == status

    def __get_role_instance_status(self, deployment, role_instance_name):
        for role_instance in deployment.role_instance_list:
            if role_instance.instance_name == role_instance_name:
                return role_instance.instance_status
        return None

        # ---------------------------------------- usage ---------------------------------------- #
        #
        # from hackathon.functions import *
        #
        #
        # def test():
        # p = PortManagement()
        #     sub_id = get_config("azure/subscriptionId")
        #     cert_path = get_config('azure/certPath')
        #     service_host_base = get_config("azure/managementServiceHostBase")
        #     t = p.connect(sub_id, cert_path, service_host_base)
        #     port = p.release_public_port('open-tech-service', 'Production', 'open-tech-role-15', 5000)
        #     print port
        #
        # if __name__ == "__main__":
        #     test()