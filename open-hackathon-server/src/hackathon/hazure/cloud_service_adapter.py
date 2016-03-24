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
from hackathon.constants import AZURE_RESOURCE_TYPE, AVMStatus
from hackathon.database import AzureKey
from hackathon.hazure.utils import find_unassigned_endpoints, add_endpoint_to_network_config
from hackathon.hazure.virtual_machine_adapter import VirtualMachineAdapter
from hackathon.template import DOCKER_UNIT

__author__ = "rapidhere"
__all__ = ["CloudServiceAdapter"]

from azure.servicemanagement.servicemanagementservice import ServiceManagementService
from azure.common import AzureHttpError, AzureMissingResourceHttpError

from service_adapter import ServiceAdapter
from constants import ASYNC_OP_RESULT


class CloudServiceAdapter(ServiceAdapter):
    """A thin wrapper on ServiceManagementServie class

    wrap up some interface to work with Azure Cloud Service
    """
    IN_PROGRESS = 'InProgress'
    SUCCEEDED = 'Succeeded'
    NOT_FOUND = 'Not found (Not Found)'
    NETWORK_CONFIGURATION = 'NetworkConfiguration'


    def __init__(self, subscription_id, cert_url, *args, **kwargs):
        super(CloudServiceAdapter, self).__init__(
            ServiceManagementService(subscription_id, cert_url, *args, **kwargs))

    def __init__(self, azure_key_id):
        azure_key = self.db.get_object(AzureKey, azure_key_id)
        super(CloudServiceAdapter, self).__init__(
            ServiceManagementService(azure_key.subscription_id, azure_key.get_local_pem_url(), host=azure_key.management_host))

    def cloud_service_exists(self, name):
        """Link to azure and check whether specific cloud service exist in specific azure subscription

        :type name: string|unicode
        :param name: the name of the coloud service

        :rtype: boolean
        :return:
        """
        try:
            props = self.service.get_hosted_service_properties(name)
        except AzureMissingResourceHttpError:
            return False
        except Exception as e:
            self.log.error(e)
            raise e

        return props is not None

    def create_cloud_service(self, name, label, location, **extra):
        """the sync version of ServiceManagementService.create_hosted_service

        for full list of arguments, please refr to ServiceManagementService.create_hosted_service

        :rtype: boolean
        :return: True on success
        """
        # DON'T DO ERROR CHECK AS azureformation.cloudService did
        # Micrsoft has checked the error up in server side
        # you don't have to do it again
        try:
            req = self.service.create_hosted_service(
                service_name=name,
                label=label,
                location=location,
                **extra)
        except AzureHttpError as e:
            self.log.debug("create cloud service %s failed: %s" % (name, e.message))
            return False

        self.log.debug("service cloud %s, creation in progress" % name)
        res = self.service.wait_for_operation_status(
            req.request_id,
            progress_callback=None,
            success_callback=None,
            failure_callback=None)

        if res and res.status == ASYNC_OP_RESULT.SUCCEEDED:
            # make sure the cloud service is here
            # it may delete by someone else
            if self.cloud_service_exists(name):
                self.log.debug("service cloud %s, creation done" % name)
                return True

        self.log.debug("service cloud %s, creation failed" % name)
        return False

    def update_cloud_service(self):
        # TODO
        raise NotImplementedError

    def delete_cloud_service(self, service_name, complete=False):
        """delete a could service on azure
        set complete to True to delete all OS/data disks

        this is a sync wrapper on ServiceManagementService.delete_hosted_service
        """
        try:
            req = self.service.delete_hosted_service(service_name, complete)
        except Exception as e:
            self.log.error("delete cloud service %s failed: %r" % (service_name, str(e)))
            raise e

        res = self.service.wait_for_operation_status(
            req.request_id,
            progress_callback=None,
            success_callback=None,
            failure_callback=None)

        if res and res.status == ASYNC_OP_RESULT.SUCCEEDED:
            self.log.debug("service cloud %s, delete done" % service_name)
        else:
            self.log.debug("service cloud %s, delete failed" % service_name)

    def is_cloud_service_locked(self, service_name):
        deployments = self.service.get_hosted_service_properties(service_name,  embed_detail=True).deployments
        for deployment in deployments:
            if deployment.locked:
                return True
        return False

    def assgin_public_endpoints(self, cloud_service_name, deployment_slot, virtual_machine_name, private_endpoints):
        """
        Assign public endpoints of cloud service for private endpoints of virtual machine
        Return None if failed
        :param cloud_service_name:
        :param deployment_slot:
        :param virtual_machine_name:
        :param private_endpoints: a list of int or str
        :return: public_endpoints: a list of int
        """
        self.log.debug('private_endpoints: %s' % private_endpoints)
        virtual_machine = VirtualMachineAdapter(self.service)
        assigned_endpoints = virtual_machine.get_assigned_endpoints(cloud_service_name)
        self.log.debug('assigned_endpoints: %s' % assigned_endpoints)
        if assigned_endpoints is None:
            self.log.debug('fail to assign endpoints: %s' % assigned_endpoints)
            return None
        public_endpoints = find_unassigned_endpoints(private_endpoints, assigned_endpoints)
        # duplicate detection for public endpoint
        self.log.debug('public_endpoints: %s' % public_endpoints)
        deployment_name = virtual_machine.get_deployment_name(cloud_service_name, deployment_slot)
        network_config = virtual_machine.get_virtual_machine_network_config(cloud_service_name,
                                                                         deployment_name,
                                                                         virtual_machine_name)
        # compose new network config to update
        new_network_config = add_endpoint_to_network_config(network_config, public_endpoints, private_endpoints)
        if new_network_config is None:
            self.log.debug('fail to assign endpoints: %s' % assigned_endpoints)
            return None
        try:
            result = virtual_machine.update_virtual_machine_network_config(cloud_service_name,
                                                                        deployment_name,
                                                                        virtual_machine_name,
                                                                        new_network_config)
        except Exception as e:
            self.log.error(e)
            self.log.error('fail to assign endpoints: %s' % assigned_endpoints)
            return None
        return public_endpoints, result

    def check_network_config(self, ctx):
        on_failed = ctx.on_failed
        on_success = ctx.on_success
        on_continue = ctx.on_continue
        if ctx.count > ctx.loop:
            self.log.error('Timed out waiting for async operation to complete.')
            self.scheduler.add_once(on_failed[0], on_failed[1], ctx.expriment.id, seconds=0)
            return

        try:
            result = self.service.get_operation_status(ctx.request_id)
            if result.status == self.IN_PROGRESS:
                self.log.debug('wait for async [%s] loop count [%d]' % (ctx.request_id, ctx.count))
                ctx.count += 1
                self.scheduler.add_once(on_continue[0], on_continue[1], ctx, seconds=10)
                return
            if result.status != self.SUCCEEDED:
                self.log.error(vars(result))
                if result.error:
                   self.log.error(result.error.code)
                   self.log.error(vars(result.error))
                self.log.error('Asynchronous operation did not succeed.')
                self.scheduler.add_once(on_failed[0], on_failed[1], ctx.experiment.id, seconds=0)
                return
            ctx.count = 0
            ctx.loop = 30
            self.scheduler.add_once(on_success[0], on_success[1], ctx, seconds=0)
        except Exception as e:
            self.log.error("Failed to config endpoint on the cloud service: %r" % str(e))
            self.scheduler.add_once(on_failed[0], on_failed[1], ctx.expriment.id, seconds=0)

    def check_virtual_machine(self, cloud_service_name, deployment_slot, ctx):
        on_failed = ctx.on_failed
        on_success = ctx.on_success
        on_continue = ctx.on_continue
        if ctx.count > ctx.loop:
            self.log.error('Timed out waiting for async operation to complete.')
            self.log.error('%s [%s] not ready' % (AZURE_RESOURCE_TYPE.VIRTUAL_MACHINE, ctx.new_name))
            self.scheduler.add_once(on_failed[0], on_failed[1], ctx.experiment.id, seconds=0)
            return

        try:
            public_endpoints = ctx.public_endpoints
            public_ports_cfg = ctx.public_ports_cfg
            virtual_machine = VirtualMachineAdapter(self.service)
            if virtual_machine.get_virtual_machine_instance_status(cloud_service_name, deployment_slot, ctx.hosted_server.vm_name) != AVMStatus.READY_ROLE:
                self.log.debug('wait for virtual machine [%r] loop count [%d]' % (ctx.new_name, ctx.count))
                ctx.count += 1
                self.scheduler.add_once(on_continue[0], on_continue[1], ctx, seconds=10)
                return
            if not isinstance(public_endpoints, list):
                self.log.debug("failed to get public ports")
                self.scheduler.add_once(on_failed[0], on_failed[1], ctx.experiment.id, seconds=0)
                return
            self.log.debug("public ports : %s" % public_endpoints)
            for i in range(len(public_ports_cfg)):
                public_ports_cfg[i][DOCKER_UNIT.PORTS_PUBLIC_PORT] = public_endpoints[i]
            self.scheduler.add_once(on_success[0], on_success[1], ctx, seconds=0)
        except Exception as e:
            self.log.error("Failed to creat virtual machine on the cloud service: %r" % str(e))
            self.scheduler.add_once(on_failed[0], on_failed[1], ctx.experiment.id, seconds=0)

