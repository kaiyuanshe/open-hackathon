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
__author__ = 'Yifu Huang'

import sys
from os.path import isfile

sys.path.append("..")
from hackathon.constants import (
    ADStatus,
)

from hackathon.azureformation.utility import (
    ASYNC_TICK,
    DEPLOYMENT_TICK,
    VIRTUAL_MACHINE_TICK,
    MDL_CLS_FUNC,
    run_job,
)


from hackathon.hmongo.models import (
    AzureKey,
)

from azure.servicemanagement import (
    ServiceManagementService,
    Deployment,
)

import time
from hackathon import Component, RequiredFeature


class Service(ServiceManagementService, Component):
    """
    Wrapper of azure service management service
    """
    IN_PROGRESS = 'InProgress'
    SUCCEEDED = 'Succeeded'
    NOT_FOUND = 'Not found (Not Found)'
    NETWORK_CONFIGURATION = 'NetworkConfiguration'

    def __init__(self, azure_key_id):
        self.azure_key_id = azure_key_id
        azure_key = self.db.get_object(AzureKey, self.azure_key_id)
        super(Service, self).__init__(azure_key.subscription_id, azure_key.get_local_pem_url(), azure_key.management_host)

    # ---------------------------------------- subscription ---------------------------------------- #

    def get_subscription(self):
        return super(Service, self).get_subscription()

    # ---------------------------------------- storage account ---------------------------------------- #

    def get_storage_account_properties(self, name):
        return super(Service, self).get_storage_account_properties(name)

    def storage_account_exists(self, name):
        """
        Check whether specific storage account exist in specific azure subscription
        :param name:
        :return:
        """
        try:
            props = self.get_storage_account_properties(name)
        except Exception as e:
            if e.message != self.NOT_FOUND:
                self.log.error(e)
            return False
        return props is not None

    def check_storage_account_name_availability(self, name):
        return super(Service, self).check_storage_account_name_availability(name)

    def create_storage_account(self, name, description, label, location):
        return super(Service, self).create_storage_account(name, description, label, location=location)

    def list_storage_accounts(self):
        return super(Service, self).list_storage_accounts()

    # ---------------------------------------- cloud service ---------------------------------------- #

    def get_hosted_service_properties(self, name, detail=False):
        return super(Service, self).get_hosted_service_properties(name, detail)

    def cloud_service_exists(self, name):
        """
        Check whether specific cloud service exist in specific azure subscription
        :param name:
        :return:
        """
        try:
            props = self.get_hosted_service_properties(name)
        except Exception as e:
            if e.message != self.NOT_FOUND:
                self.log.error(e)
            return False
        return props is not None

    def check_hosted_service_name_availability(self, name):
        return super(Service, self).check_hosted_service_name_availability(name)

    def create_hosted_service(self, name, label, location):
        return super(Service, self).create_hosted_service(name, label, location=location)

    # ---------------------------------------- deployment ---------------------------------------- #

    def get_deployment_by_slot(self, cloud_service_name, deployment_slot):
        return super(Service, self).get_deployment_by_slot(cloud_service_name, deployment_slot)

    def get_deployment_by_name(self, cloud_service_name, deployment_name):
        return super(Service, self).get_deployment_by_name(cloud_service_name, deployment_name)

    def deployment_exists(self, cloud_service_name, deployment_slot):
        try:
            props = self.get_deployment_by_slot(cloud_service_name, deployment_slot)
        except Exception as e:
            if e.message != self.NOT_FOUND:
                self.log.error(e)
            return False
        return props is not None

    def get_deployment_name(self, cloud_service_name, deployment_slot):
        try:
            props = self.get_deployment_by_slot(cloud_service_name, deployment_slot)
        except Exception as e:
            self.log.error(e)
            return None
        return None if props is None else props.name

    def wait_for_deployment(self, cloud_service_name, deployment_name, second_per_loop, loop, status=ADStatus.RUNNING):
        count = 0
        props = self.get_deployment_by_name(cloud_service_name, deployment_name)
        if props is None:
            return False
        while props.status != status:
            self.log.debug('wait for deployment [%s] loop count: %d' % (deployment_name, count))
            count += 1
            if count > loop:
                self.log.error('Timed out waiting for deployment status.')
                return False
            time.sleep(second_per_loop)
            props = self.get_deployment_by_name(cloud_service_name, deployment_name)
            if props is None:
                return False
        return props.status == status

    def get_deployment_dns(self, cloud_service_name, deployment_slot):
        try:
            props = self.get_deployment_by_slot(cloud_service_name, deployment_slot)
        except Exception as e:
            self.log.error(e)
            return None
        return None if props is None else props.url

    # ---------------------------------------- virtual machine ---------------------------------------- #

    def create_virtual_machine_deployment(self,
                                          cloud_service_name,
                                          deployment_name,
                                          deployment_slot,
                                          virtual_machine_label,
                                          virtual_machine_name,
                                          system_config,
                                          os_virtual_hard_disk,
                                          network_config,
                                          virtual_machine_size,
                                          vm_image_name):
        return super(Service, self).create_virtual_machine_deployment(cloud_service_name,
                                                                      deployment_name,
                                                                      deployment_slot,
                                                                      virtual_machine_label,
                                                                      virtual_machine_name,
                                                                      system_config,
                                                                      os_virtual_hard_disk,
                                                                      network_config=network_config,
                                                                      role_size=virtual_machine_size,
                                                                      vm_image_name=vm_image_name)

    def get_virtual_machine_instance_status(self, deployment, virtual_machine_name):
        if deployment is not None and isinstance(deployment, Deployment):
            for role_instance in deployment.role_instance_list:
                if role_instance.instance_name == virtual_machine_name:
                    return role_instance.instance_status
        return None

    def wait_for_virtual_machine(self,
                                 cloud_service_name,
                                 deployment_name,
                                 virtual_machine_name,
                                 second_per_loop,
                                 loop,
                                 status):
        count = 0
        props = self.get_deployment_by_name(cloud_service_name, deployment_name)
        while self.get_virtual_machine_instance_status(props, virtual_machine_name) != status:
            self.log.debug('wait for virtual machine [%s] loop count: %d' % (virtual_machine_name, count))
            count += 1
            if count > loop:
                self.log.error('Timed out waiting for role instance status.')
                return False
            time.sleep(second_per_loop)
            props = self.get_deployment_by_name(cloud_service_name, deployment_name)
        return self.get_virtual_machine_instance_status(props, virtual_machine_name) == status

    def update_virtual_machine_network_config(self,
                                              cloud_service_name,
                                              deployment_name,
                                              virtual_machine_name,
                                              network_config):
        return super(Service, self).update_role(cloud_service_name,
                                                deployment_name,
                                                virtual_machine_name,
                                                network_config=network_config)

    def get_virtual_machine_public_endpoint(self,
                                            cloud_service_name,
                                            deployment_name,
                                            virtual_machine_name,
                                            endpoint_name):
        deployment = self.get_deployment_by_name(cloud_service_name, deployment_name)
        for role in deployment.role_instance_list:
            if role.role_name == virtual_machine_name:
                if role.instance_endpoints is not None:
                    for instance_endpoint in role.instance_endpoints:
                        if instance_endpoint.name == endpoint_name:
                            return instance_endpoint.public_port
        return None

    def get_virtual_machine_public_ip(self, cloud_service_name, deployment_name, virtual_machine_name):
        deployment = self.get_deployment_by_name(cloud_service_name, deployment_name)
        for role in deployment.role_instance_list:
            if role.role_name == virtual_machine_name:
                if role.instance_endpoints is not None:
                    return role.instance_endpoints.instance_endpoints[0].vip
        return None

    def get_virtual_machine_private_ip(self, cloud_service_name, deployment_name, virtual_machine_name):
        deployment = self.get_deployment_by_name(cloud_service_name, deployment_name)
        for role in deployment.role_instance_list:
            if role.role_name == virtual_machine_name:
                return role.ip_address
        return None

    def get_virtual_machine(self, cloud_service_name, deployment_name, role_name):
        return super(Service, self).get_role(cloud_service_name, deployment_name, role_name)

    def virtual_machine_exists(self, cloud_service_name, deployment_name, virtual_machine_name):
        try:
            props = self.get_virtual_machine(cloud_service_name, deployment_name, virtual_machine_name)
        except Exception as e:
            if e.message != self.NOT_FOUND:
                self.log.error(e)
            return False
        return props is not None

    def add_virtual_machine(self,
                            cloud_service_name,
                            deployment_name,
                            virtual_machine_name,
                            system_config,
                            os_virtual_hard_disk,
                            network_config,
                            virtual_machine_size,
                            vm_image_name):
        return super(Service, self).add_role(cloud_service_name,
                                             deployment_name,
                                             virtual_machine_name,
                                             system_config,
                                             os_virtual_hard_disk,
                                             network_config=network_config,
                                             role_size=virtual_machine_size,
                                             vm_image_name=vm_image_name)

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

    def stop_virtual_machine(self, cloud_service_name, deployment_name, virtual_machine_name, type):
        return super(Service, self).shutdown_role(cloud_service_name, deployment_name, virtual_machine_name, type)

    def start_virtual_machine(self, cloud_service_name, deployment_name, virtual_machine_name):
        return super(Service, self).start_role(cloud_service_name, deployment_name, virtual_machine_name)

    # ---------------------------------------- endpoint ---------------------------------------- #

    def get_assigned_endpoints(self, cloud_service_name):
        """
        Return a list of assigned endpoints of given cloud service
        :param cloud_service_name:
        :return: endpoints: a list of int
        """
        properties = self.get_hosted_service_properties(cloud_service_name, True)
        endpoints = []
        for deployment in properties.deployments.deployments:
            for role in deployment.role_list.roles:
                for configuration_set in role.configuration_sets.configuration_sets:
                    if configuration_set.configuration_set_type == self.NETWORK_CONFIGURATION:
                        if configuration_set.input_endpoints is not None:
                            for input_endpoint in configuration_set.input_endpoints.input_endpoints:
                                endpoints.append(input_endpoint.port)
        return map(int, endpoints)

    # ---------------------------------------- other ---------------------------------------- #

    def get_operation_status(self, request_id):
        return super(Service, self).get_operation_status(request_id)

    def wait_for_async(self, request_id, second_per_loop, loop):
        """
        Wait for async operation, up to second_per_loop * loop
        :param request_id:
        :return:
        """
        count = 0
        result = self.get_operation_status(request_id)
        while result.status == self.IN_PROGRESS:
            self.log.debug('wait for async [%s] loop count [%d]' % (request_id, count))
            count += 1
            if count > loop:
                self.log.error('Timed out waiting for async operation to complete.')
                return False
            time.sleep(second_per_loop)
            result = self.get_operation_status(request_id)
        if result.status != self.SUCCEEDED:
            self.log.error(vars(result))
            if result.error:
                self.log.error(result.error.code)
                self.log.error(vars(result.error))
            self.log.error('Asynchronous operation did not succeed.')
            return False
        return True

    def ping(self):
        """
        Use list storage accounts to check azure service management service health
        :return:
        """
        try:
            self.list_storage_accounts()
        except Exception as e:
            self.log.error(e)
            return False
        return True

    # ---------------------------------------- call ---------------------------------------- #

    def query_async_operation_status(self, request_id,
                                     true_mdl_cls_func, true_cls_args, true_func_args,
                                     false_mdl_cls_func, false_cls_args, false_func_args):
        self.log.debug('query async operation status: request_id [%s]' % request_id)
        result = self.get_operation_status(request_id)
        if result.status == self.IN_PROGRESS:
            # query async operation status
            run_job(MDL_CLS_FUNC[2],
                    (self.azure_key_id, ),
                    (request_id,
                     true_mdl_cls_func, true_cls_args, true_func_args,
                     false_mdl_cls_func, false_cls_args, false_func_args),
                    ASYNC_TICK)
        elif result.status == self.SUCCEEDED:
            run_job(true_mdl_cls_func, true_cls_args, true_func_args)
        else:
            run_job(false_mdl_cls_func, false_cls_args, false_func_args)

    def query_deployment_status(self, cloud_service_name, deployment_name,
                                true_mdl_cls_func, true_cls_args, true_func_args):
        self.log.debug('query deployment status: deployment_name [%s]' % deployment_name)
        result = self.get_deployment_by_name(cloud_service_name, deployment_name)
        if result.status == ADStatus.RUNNING:
            run_job(true_mdl_cls_func, true_cls_args, true_func_args)
        else:
            # query deployment status
            run_job(MDL_CLS_FUNC[15],
                    (self.azure_key_id, ),
                    (cloud_service_name, deployment_name,
                     true_mdl_cls_func, true_cls_args, true_func_args),
                    DEPLOYMENT_TICK)

    def query_virtual_machine_status(self, cloud_service_name, deployment_name, virtual_machine_name, status,
                                     true_mdl_cls_func, true_cls_args, true_func_args):
        self.log.debug('query virtual machine status: virtual_machine_name [%s]' % virtual_machine_name)
        deployment = self.get_deployment_by_name(cloud_service_name, deployment_name)
        result = self.get_virtual_machine_instance_status(deployment, virtual_machine_name)
        if result == status:
            run_job(true_mdl_cls_func, true_cls_args, true_func_args)
        else:
            # query virtual machine status
            run_job(MDL_CLS_FUNC[8],
                    (self.azure_key_id, ),
                    (cloud_service_name, deployment_name, virtual_machine_name, status,
                     true_mdl_cls_func, true_cls_args, true_func_args),
                    VIRTUAL_MACHINE_TICK)