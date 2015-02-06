__author__ = 'Yifu Huang'

import sys

sys.path.append("..")
from hackathon.log import *
from hackathon.functions import *
from azure.servicemanagement import *
import time


class PortManagement():
    def __init__(self):
        self.sms = None

    def connect(self, subscription_id, pem_url, management_host):
        try:
            self.sms = ServiceManagementService(subscription_id, pem_url, management_host)
        except Exception as e:
            log.error(e)
            return False
        return True

    def assign_public_port(self, cloud_service_name, deployment_slot, virtual_machine_name, private_port):
        assigned_ports = self.__get_assigned_ports(cloud_service_name)
        # duplicate detection for public port
        public_port = int(private_port)
        while str(public_port) in assigned_ports:
            public_port = (public_port + 1) % 65536
        # compose network config to update
        deployment = self.sms.get_deployment_by_slot(cloud_service_name, deployment_slot)
        network = self.__compose_network_config(cloud_service_name,
                                                deployment.name,
                                                virtual_machine_name,
                                                public_port,
                                                private_port)
        result = self.sms.update_role(cloud_service_name,
                                      deployment.name,
                                      virtual_machine_name,
                                      network_config=network)
        self.__wait_for_async(result.request_id, 5, 100)
        self.__wait_for_role(cloud_service_name,
                             deployment.name,
                             virtual_machine_name,
                             5,
                             100)
        return public_port

    # ---------------------------------------- helper functions ---------------------------------------- #

    def __get_assigned_ports(self, cloud_service_name):
        properties = self.sms.get_hosted_service_properties(cloud_service_name, True)
        ports = []
        for deployment in properties.deployments.deployments:
            for role in deployment.role_list.roles:
                for configuration_set in role.configuration_sets.configuration_sets:
                    if configuration_set.configuration_set_type == 'NetworkConfiguration':
                        if configuration_set.input_endpoints is not None:
                            for input_endpoint in configuration_set.input_endpoints.input_endpoints:
                                ports.append(input_endpoint.port)
        return ports

    def __compose_network_config(self, cloud_service_name, deployment_name, virtual_machine_name,
                                 public_port, private_port):
        virtual_machine = self.sms.get_role(cloud_service_name, deployment_name, virtual_machine_name)
        network = ConfigurationSet()
        network.configuration_set_type = 'NetworkConfiguration'
        for configuration_set in virtual_machine.configuration_sets.configuration_sets:
            if configuration_set.configuration_set_type == 'NetworkConfiguration':
                for input_endpoint in configuration_set.input_endpoints.input_endpoints:
                    network.input_endpoints.input_endpoints.append(
                        ConfigurationSetInputEndpoint(input_endpoint.name,
                                                      input_endpoint.protocol,
                                                      input_endpoint.port,
                                                      input_endpoint.local_port)
                    )
                break
        network.input_endpoints.input_endpoints.append(
            ConfigurationSetInputEndpoint('auto-' + str(public_port), 'tcp', str(public_port), str(private_port))
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

# p = PortManagement()
# sub_id = get_config("azure/subscriptionId")
# cert_path = get_config('azure/certPath')
# service_host_base = get_config("azure/managementServiceHostBase")
# t = p.connect(sub_id, cert_path, service_host_base)
# public_port = p.assign_public_port('open-tech-service', 'Production', 'open-tech-role-4', 3389)
# print public_port