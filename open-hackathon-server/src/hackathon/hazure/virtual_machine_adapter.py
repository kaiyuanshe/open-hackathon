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

__author__ = "rapidhere"
__all__ = ["VirtualMachineAdapter"]

from azure.servicemanagement.servicemanagementservice import ServiceManagementService, Deployment
from azure.common import AzureMissingResourceHttpError

from service_adapter import ServiceAdapter
from constants import ASYNC_OP_RESULT


class VirtualMachineAdapter(ServiceAdapter):
    """A thin wrapper on ServiceManagementServie class

    wrap up some interface to work with Azure Virtual Machine

    NOTE: the deployment must be done on a cloud service in Azure, and used in a virtual machine,
    so we won't split a signle deployment adapter, instead, we do it in this adapter
    """
    NETWORK_CONFIGURATION = 'NetworkConfiguration'

    def __init__(self, subscription_id, cert_url, *args, **kwargs):
        super(VirtualMachineAdapter, self).__init__(
            ServiceManagementService(subscription_id, cert_url, *args, **kwargs))

    def deployment_exists(self, cloud_service_name, deployment_slot):
        """check if the specified cloud service is under specified deployment slot(production or staging)

        :rtype: boolean
        :return: True if deployment_slot exists; NOTE if the cloud service not exists, will return False
        """
        try:
            props = self.service.get_deployment_by_slot(cloud_service_name, deployment_slot)
        except AzureMissingResourceHttpError:
            return False
        except Exception as e:
            self.log.error(e)
            raise e

        return props is not None

    def get_deployment_name(self, cloud_service_name, deployment_slot):
        """get the cloud service's deployment's name under slot
        """
        try:
            props = self.service.get_deployment_by_slot(cloud_service_name, deployment_slot)
        except Exception as e:
            self.log.error(e)
            raise e
        return None if props is None else props.name

    def get_deployment_by_name(self, cloud_service_name, deployment_name):
        """get the deployment's properties by it's name
        """
        try:
            return self.service.get_deployment_by_name(cloud_service_name, deployment_name)
        except Exception as e:
            self.log.error(e)
            raise e

    def get_deployment_by_slot(self, cloud_service_name, deployment_slot):
        """get the deployment's properties by it's slot
        """
        try:
            return self.service.get_deployment_by_slot(cloud_service_name, deployment_slot)
        except Exception as e:
            self.log.error(e)
            raise e

    def virtual_machine_exists(self, cloud_service_name, deployment_name, role_name):
        """check if the specified virtual machine exists

        :rtype: boolean
        :return: True if virtual machine exists; NOTE if the cloud service or deployment not exists, will return False
        """
        try:
            props = self.service.get_role(cloud_service_name, deployment_name, role_name)
        except AzureMissingResourceHttpError:
            return False
        except Exception as e:
            self.log.error(e)
            raise e

        return props is not None

    def get_virtual_machine_instance_status(self, cloud_service_name, deployment_slot, vm_name):
        """get the virtual machine instance named vm_name's status under deployment
        """
        props = self.get_deployment_by_slot(cloud_service_name, deployment_slot)

        if not props or not isinstance(props, Deployment):
            return None

        for role_instance in props.role_instance_list:
            if role_instance.instance_name == vm_name:
                return role_instance.instance_status

        return None

    def add_virtual_machine(self, *args, **kwargs):
        """a thin wrap on ServiceManagementService.add_role
        """
        return self.service.add_role(*args, **kwargs)

    def stop_virtual_machine(self, *args, **kwargs):
        """a thin wrap on ServiceManagementService.shutdown_role
        """
        return self.service.shutdown_role(*args, **kwargs)

    def update_virtual_machine_network_config(
            self, cloud_service_name, deployment_name, virtual_machine_name, network_config):
        """update the network config of a vm
        """
        return self.service.update_role(
            cloud_service_name,
            deployment_name,
            virtual_machine_name,
            network_config=network_config)

    def get_assigned_endpoints(self, cloud_service_name):
        """Return a list of assigned endpoints of given cloud service

        if cloud service not exists, will raise a exception

        :return: endpoints: a list of int
        """
        properties = self.service.get_hosted_service_properties(cloud_service_name, True)
        endpoints = []
        for deployment in properties.deployments.deployments:
            for role in deployment.role_list.roles:
                for configuration_set in role.configuration_sets.configuration_sets:
                    if configuration_set.configuration_set_type == "NetworkConfiguration":
                        if configuration_set.input_endpoints is not None:
                            for input_endpoint in configuration_set.input_endpoints.input_endpoints:
                                endpoints.append(input_endpoint.port)
        return map(int, endpoints)

    def get_virtual_machine_role(self, cloud_service_name, deployment_name, virtual_machine_name):
        """get the role instance of vm

        return None if not found
        """
        deployment = self.get_deployment_by_name(cloud_service_name, deployment_name)
        for role in deployment.role_instance_list:
            if role.role_name == virtual_machine_name:
                return role

        return None

    def get_virtual_machine_public_ip(self, cloud_service_name, deployment_name, virtual_machine_name):
        """get the public ip of the virtual machine

        return None if not found
        """
        # TODO: full copy from azureformation module, is this way of finding public ip correct?
        deployment = self.get_deployment_by_name(cloud_service_name, deployment_name)
        for role in deployment.role_instance_list:
            if role.role_name == virtual_machine_name:
                if role.instance_endpoints is not None:
                    return role.instance_endpoints.instance_endpoints[0].vip
        return None

    def get_virtual_machine_public_endpoint(
            self, cloud_service_name, deployment_name, virtual_machine_name, endpoint_name):
        """get the (public_ip, public_port) of the virtual machine on specified endpoint

        return (None, None) if not find
        """
        deployment = self.get_deployment_by_name(cloud_service_name, deployment_name)
        for role in deployment.role_instance_list:
            if role.role_name == virtual_machine_name:
                if role.instance_endpoints is not None:
                    for instance_endpoint in role.instance_endpoints:
                        if instance_endpoint.name == endpoint_name:
                            return instance_endpoint.vip, instance_endpoint.public_port
        return None, None

    def delete_virtual_machine(self, service_name, deployment_name, role_name, complete=False):
        """delete a virutal machine from azure

        this is the sync wrapper of ServiceManagementService.delete_role
        """
        try:
            req = self.service.delete_role(service_name, deployment_name, role_name, complete=complete)
        except Exception as e:
            self.log.error("delete vm %s failed: %r" % (role_name, str(e)))
            raise e

        res = self.service.wait_for_operation_status(
            req.request_id,
            progress_callback=None,
            success_callback=None,
            failure_callback=None)

        if res and res.status == ASYNC_OP_RESULT.SUCCEEDED:
            self.log.debug("vm %s, delete done" % role_name)
        else:
            self.log.debug("vm %s, delete failed" % role_name)

    def delete_deployment(self, service_name, deployment_name, complete=False):
        """delete a deployment from azure

        this is the sync wrapper of ServiceManagementService.delete_deployment
        """
        try:
            req = self.service.delete_deployment(service_name, deployment_name, delete_vhd=complete)
        except Exception as e:
            self.log.error("delete deployment %s failed: %r" % (deployment_name, str(e)))
            raise e

        res = self.service.wait_for_operation_status(
            req.request_id,
            progress_callback=None,
            success_callback=None,
            failure_callback=None)

        if res and res.status == ASYNC_OP_RESULT.SUCCEEDED:
            self.log.debug("deployment %s, delete done" % deployment_name)
        else:
            self.log.debug("deployment %s, delete failed" % deployment_name)

    def get_virtual_machine_network_config(self, cloud_service_name, deployment_name, virtual_machine_name):
        try:
            virtual_machine = self.get_virtual_machine(cloud_service_name, deployment_name, virtual_machine_name)
        except Exception as e:
            self.log.error(e)
            return None
        if virtual_machine is not None:
            for configuration_set in virtual_machine.configuration_sets.configuration_sets:
                if configuration_set.configuration_set_type == self.NETWORK_CONFIGURATION:
                    return configuration_set
        return None

    def get_virtual_machine(self, cloud_service_name, deployment_name, role_name):
        return self.service.get_role(cloud_service_name, deployment_name, role_name)
