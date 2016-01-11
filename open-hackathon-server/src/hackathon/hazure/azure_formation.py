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
__all__ = ["AzureFormation"]

import json

from hackathon import Component, Context, RequiredFeature
from hackathon.database import AzureCloudService, AzureStorageAccount, VirtualEnvironment
from hackathon.constants import (
    ACSStatus, ASAStatus, ADStatus, AVMStatus, VEStatus, EStatus)

from cloud_service_adapter import CloudServiceAdapter
from storage_account_adapter import StorageAcountAdapter
from virtual_machine_adapter import VirtualMachineAdapter
from utils import get_network_config, get_remote_parameters
from constants import ASYNC_OP_QUERY_INTERVAL, ASYNC_OP_RESULT, ASYNC_OP_QUERY_INTERVAL_LONG


class AzureFormation(Component):
    """The high level Azure Resource Manager

    the main purpose of this class is to manage the Azure VirtualMachine
    but Azure VirtualMachine depends on lots of Azure Resources like CloudService and Deployment
    this class will manage all of this resouces, like a formation of Azure Resources

    dislike the old AzureFormation class, this class depend on independ Azure Service Adapters to
    finish its job, this is just a high level intergration of these adapters

    usage: RequiredFeature("azuire_formation").setup(template_unit)
    """
    # NOTE: the only purpose of use exprmgr is to update the
    # status of experiment, see the function __setup_virtual_machine_done
    # this requirment will be removed in future after callbacks have been implied
    expr_manager = RequiredFeature("expr_manager")

    def __init__(self):
        pass

    def start_vm(self, resource_id, azure_key, template_units, virtual_environments):
        """setup the resources needed by the template unit and start the virtual machine

        this will create the missed VirtualMachine, CloudService and Storages
        this function is not blocked, it will run in the background and return immediatly

        :param resouce_id: a integer that can indentify the creation of azure resource, is reusable to checkout created virtual machine name
        :param template_units: the azure template units, contains the data need by azure formation
        :param azure_key: the azure_key object, use to access azure
        :param virtual_environments: the virtual envrionments associated with this setup NOTE: this is a workaround
        """
        # the setup of each unit must be SERLIALLY EXECUTED
        # to avoid the creation of same resource in same time
        # TODO: we still have't avoid the parrallel excution of the setup of same template
        job_ctxs = []
        ctx = Context(job_ctxs=job_ctxs, current_job_index=0, resource_id=resource_id)

        assert len(template_units) == len(virtual_environments)

        for i in xrange(0, len(template_units)):
            unit = template_units[i]
            ve = virtual_environments[i]

            name = self.get_virtual_machine_name(unit.get_virtual_machine_name(), resource_id)

            # construct current virutal envrionment's context
            job_ctxs.append(Context(
                cloud_service_name=unit.get_cloud_service_name(),
                cloud_service_label=unit.get_cloud_service_label(),
                cloud_service_host=unit.get_cloud_service_location(),

                storage_account_name=unit.get_storage_account_name(),
                storage_account_description=unit.get_storage_account_description(),
                storage_account_label=unit.get_storage_account_label(),
                storage_account_location=unit.get_storage_account_location(),

                virtual_machine_name=name,
                virtual_machine_label=unit.get_virtual_machine_label(),
                deployment_name=unit.get_deployment_name(),
                deployment_slot=unit.get_deployment_slot(),
                system_config=unit.get_system_config(),
                raw_system_config=unit.get_raw_system_config(),
                os_virtual_hard_disk=unit.get_os_virtual_hard_disk(),
                virtual_machine_size=unit.get_virtual_machine_size(),
                image_name=unit.get_image_name(),
                raw_network_config=unit.get_raw_network_config(),
                is_vm_image=unit.is_vm_image(),
                remote=unit.get_remote(),
                endpoint_name=unit.get_remote_port_name(),

                # NOTE: ONLY callback purpose functions can depend on virutal_environment_id
                virtual_environment_id=ve.id,

                azure_key_id=azure_key.id,
                subscription_id=azure_key.subscription_id,
                pem_url=azure_key.pem_url,
                management_host=azure_key.management_host))

        # execute from first job context
        self.__schedule_setup(ctx)

    def stop_vm(self):
        """stop the virtual machine
        """
        pass

    def get_virtual_machine_name(self, virtual_machine_base_name, resource_id):
        """retrieve the virtual machine name by resource_id

        resource_id is used by azure_formation.setup
        """
        return "%s-%d" % (virtual_machine_base_name, int(resource_id))

    # private functions
    def __schedule_setup(self, sctx):
        self.scheduler.add_once("azure_formation", "schedule_setup", context=sctx, seconds=0)

    def schedule_setup(self, ctx):
        current_job_index = ctx.current_job_index
        job_ctxs = ctx.job_ctxs

        if current_job_index >= len(job_ctxs):
            self.log.debug("azure virtual environment setup finish")
            return True

        # excute current setup from setup cloud service
        # whole stage:
        #   setup_cloud_service -> setup_storage -> setup_virtual_machine ->(index + 1) schedule_setup
        # on whatever stage when error occurs, will turn into __on_setup_failed
        self.log.debug(
            "azure virtual environment %d: '%r' setup progress begin" %
            (current_job_index, job_ctxs[current_job_index]))
        self.scheduler.add_once("azure_formation", "setup_cloud_service", context=ctx, seconds=0)

    def setup_cloud_service(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = CloudServiceAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        name = ctx.cloud_service_name
        label = ctx.cloud_service_label
        location = ctx.cloud_service_host
        azure_key_id = ctx.azure_key_id

        try:
            if not adapter.cloud_service_exists(name):
                if not adapter.create_cloud_service(
                        name=name,
                        label=label,
                        location=location):
                    self.log.error("azure virtual environment %d create remote cloud service failed via creation" %
                                   sctx.current_job_index)
                    self.__on_setup_failed(sctx)
                    return

                # first delete the possible old CloudService
                # TODO: is this necessary?
                self.db.delete_all_objects_by(AzureCloudService, name=name)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d create remote cloud service failed: %r"
                % (sctx.current_job_index, str(e)))
            self.__on_setup_failed(sctx)
            return

        # update the table
        if self.db.count_by(AzureCloudService, name=name) == 0:
            self.db.add_object_kwargs(
                AzureCloudService,
                name=name,
                label=label,
                location=location,
                status=ACSStatus.CREATED,
                azure_key_id=azure_key_id)

        # commit changes
        self.db.commit()
        self.log.debug("azure virtual environment %d cloud service setup done" % sctx.current_job_index)

        # next step: setup storage
        self.scheduler.add_once("azure_formation", "setup_storage", context=sctx, seconds=0)
        return

    def setup_storage(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = StorageAcountAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        name = ctx.storage_account_name
        label = ctx.storage_account_label
        location = ctx.storage_account_location
        description = ctx.storage_account_description
        azure_key_id = ctx.azure_key_id

        try:
            if not adapter.storage_account_exists(name):
                # TODO: use the async way
                if not adapter.create_storage_account(name, description, label, location):
                    self.log.error("azure virtual environment %d create storage account failed via creation" %
                                   sctx.current_job_index)
                    self.__on_setup_failed(sctx)
                    return

                # delete possible old accounts
                self.db.delete_all_objects_by(AzureStorageAccount, name=name)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d create storage account failed: %r"
                % (sctx.current_job_index, str(e)))
            self.__on_setup_failed(sctx)
            return

        if self.db.count_by(AzureStorageAccount, name=name) != 0:
            self.db.add_object_kwargs(
                AzureStorageAccount,
                name=name,
                description=description,
                label=label,
                location=location,
                status=ASAStatus.ONLINE,
                azure_key_id=azure_key_id)

        self.db.commit()
        self.log.debug("azure virtual environment %d storage setup done" % sctx.current_job_index)

        # next step: setup virtual machine
        self.scheduler.add_once("azure_formation", "setup_virtual_machine", context=sctx, seconds=0)

    def setup_virtual_machine(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]

        adapter = VirtualMachineAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        if adapter.deployment_exists(ctx.cloud_service_name, ctx.deployment_slot):
            # TODO: need to store the deployment info into db?
            self.__setup_virtual_machine_with_deployment_existed(sctx)
        else:
            self.__setup_virtual_machine_without_deployment_existed(sctx)

    def __setup_virtual_machine_with_deployment_existed(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]

        adapter = VirtualMachineAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        deployment_name = adapter.get_deployment_name(ctx.cloud_service_name, ctx.deployment_slot)
        if not ctx.is_vm_image:
            network_config = get_network_config(
                ctx.raw_network_config,
                adapter.get_assigned_endpoints(ctx.cloud_service_name))
        else:
            network_config = None

        # add virtual machine to deployment
        try:
            # create if vm is not created
            if not adapter.virtual_machine_exists(ctx.cloud_service_name, deployment_name, ctx.virtual_machine_name):
                req = adapter.add_virtual_machine(
                    ctx.cloud_service_name,
                    deployment_name,
                    ctx.virtual_machine_name,
                    ctx.system_config,
                    ctx.os_virtual_hard_disk,
                    network_config=network_config,
                    role_size=ctx.virtual_machine_size,
                    vm_image_name=ctx.image_name if ctx.is_vm_image else None)
            # NOTE: if the vm is created, we think is well configured
            # else:  # if vm is created, then we need to config the vm
            #    ctx.vm_need_config = True
            #    self.__wait_for_virtual_machine_ready(sctx)
            #    return
            else:
                self.__setup_virtual_machine_done(sctx)
                return
        except Exception as e:
            self.log.error(
                "azure virtual environment %d create virtual machine %r failed: %r"
                % (sctx.current_job_index, ctx.virtual_machine_name, str(e)))
            self.__on_setup_failed(sctx)
            return

        # wait for add virtual machine to finish
        ctx.request_id = req.request_id
        ctx.vm_need_config = True if ctx.is_vm_image else False
        self.__wait_for_add_virtual_machine(sctx)

    def __setup_virtual_machine_without_deployment_existed(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]

        adapter = VirtualMachineAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        if not ctx.is_vm_image:
            network_config = get_network_config(
                ctx.raw_network_config,
                adapter.get_assigned_endpoints(ctx.cloud_service_name))
        else:
            network_config = None

        try:
            req = adapter.create_virtual_machine_deployment(
                ctx.cloud_service_name,
                ctx.deployment_name,
                ctx.deployment_slot,
                ctx.virtual_machine_label,
                ctx.virtual_machine_name,
                ctx.system_config,
                ctx.os_virtual_hard_disk,
                network_config,
                role_size=ctx.virtual_machine_size,
                vm_image_name=ctx.image_name if ctx.is_vm_image else None)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d create virtual machine %r failed: %r"
                % (sctx.current_job_index, ctx.virtual_machine_name, str(e)))
            self.__on_setup_failed(sctx)
            return

        # wait for add virtual machine to finish
        ctx.request_id = req.request_id
        ctx.vm_need_config = True if ctx.is_vm_image else False
        self.__wait_for_create_virtual_machine_deployment(sctx)

    def __check_vm_operation_status(self, sctx, on_success, on_failed, on_continue):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = VirtualMachineAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        res = adapter.get_operation_status(ctx.request_id)

        if res.status == ASYNC_OP_RESULT.SUCCEEDED:
            on_success(sctx)
        elif res.error:
            on_failed(sctx)
        else:
            on_continue(sctx)

    def __wait_for_add_virtual_machine(self, sctx):
        self.log.debug("azure virtual environment: %d, waiting for add virtual machine" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_formation", "wait_for_add_virtual_machine",
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_add_virtual_machine(self, sctx):
        self.__check_vm_operation_status(
            sctx,
            self.__wait_for_virtual_machine_ready,
            self.__on_setup_failed,
            self.__wait_for_add_virtual_machine)

    def __wait_for_create_virtual_machine_deployment(self, sctx):
        self.log.debug("azure virtual environment: %d, waiting for create vm_deployment" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_formation", "wait_for_create_virtual_machine_deployment",
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_create_virtual_machine_deployment(self, sctx):
        self.__check_vm_operation_status(
            sctx,
            self.__wait_for_deployment_ready,
            self.__on_setup_failed,
            self.__wait_for_create_virtual_machine_deployment)

    def __config_virtual_machine(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        ctx.vm_need_config = False
        adapter = VirtualMachineAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        network_config = get_network_config(
            ctx.raw_network_config,
            adapter.get_assigned_endpoints(ctx.cloud_service_name))

        if len(network_config.input_endpoints.input_endpoints) == 0:
            # don't need to config, skip
            self.__setup_virtual_machine_done(sctx)
            return

        try:
            req = adapter.update_virtual_machine_network_config(
                ctx.cloud_service_name,
                ctx.deployment_name,
                ctx.virtual_machine_name,
                network_config)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d error while config network: %r" %
                (sctx.current_job_index, e.message))
            self.__on_setup_failed(sctx)
            return

        ctx.request_id = req.request_id
        self.__wait_for_config_virtual_machine(sctx)

    def __wait_for_config_virtual_machine(self, sctx):
        self.log.debug("azure virtual environment: %d, waiting for configure network" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_formation", "wait_for_config_virtual_machine",
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_config_virtual_machine(self, sctx):
        self.__check_vm_operation_status(
            sctx,
            self.__wait_for_virtual_machine_ready,
            self.__on_setup_failed,
            self.__wait_for_config_virtual_machine)

    def __wait_for_deployment_ready(self, sctx):
        self.log.debug("azure virtual environment: %d, waiting for deployment ready" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_formation", "wait_for_deployment_ready",
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_deployment_ready(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = VirtualMachineAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        props = adapter.get_deployment_by_slot(ctx.cloud_service_name, ctx.deployment_slot)

        if not props:
            self.log.error(
                "azure virtual environment %d error occured while waiting for deployment ready"
                % sctx.current_job_index)
            self.__on_setup_failed(sctx)
            return

        if props.status == ADStatus.RUNNING:
            self.__wait_for_virtual_machine_ready(sctx)
        else:
            self.__wait_for_create_virtual_machine_deployment(sctx)

    def __wait_for_virtual_machine_ready(self, sctx):
        self.log.debug("azure virtual environment: %d, waiting for vm ready" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_formation", "wait_for_virtual_machine_ready",
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL_LONG)

    def wait_for_virtual_machine_ready(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = VirtualMachineAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        status = adapter.get_virtual_machine_instance_status(
            ctx.cloud_service_name, ctx.deployment_slot, ctx.virtual_machine_name)

        if not status:
            self.log.error(
                "azure virtual environment %d error occured while waiting for virtual machine ready"
                % sctx.current_job_index)
            self.__on_setup_failed(sctx)
            return

        self.log.debug(
            "waiting for virtual machine ready, vm: %s, status: %s" %
            (ctx.virtual_machine_name, str(status)))
        if status == AVMStatus.READY_ROLE:
            if ctx.vm_need_config:
                ctx.vm_need_config = False
                self.__config_virtual_machine(sctx)
            else:
                self.__setup_virtual_machine_done(sctx)
        else:
            self.__wait_for_virtual_machine_ready(sctx)

    # callbacks will be called here
    def __on_setup_failed(self, sctx):
        try:
            self.log.debug("azure virtual environment %d vm setup failed" % sctx.current_job_index)
            # TODO: rollback

            ctx = sctx.job_ctxs[sctx.current_job_index]
            ve = self.db.find_first_object_by(VirtualEnvironment, id=ctx.virtual_environment_id)

            if ve:
                ve.status = VEStatus.FAILED
                ve.experiment.status = EStatus.FAILED
                self.db.commit()
        finally:
            self.log.debug("azure virtual environment %d vm fail callback done, step to next" % sctx.current_job_index)
            # after rollback done, step into next unit
            sctx.current_job_index += 1
            self.__schedule_setup(sctx)

    def __setup_virtual_machine_done(self, sctx):
        self.log.debug("azure virtual environment %d vm setup done" % sctx.current_job_index)
        ctx = sctx.job_ctxs[sctx.current_job_index]

        # update the status of virtual environment
        ve = self.db.find_first_object_by(VirtualEnvironment, id=ctx.virtual_environment_id)

        adapter = VirtualMachineAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)
        if ve:
            ve.status = VEStatus.RUNNING

            public_ip, port = adapter.get_virtual_machine_public_endpoint(
                ctx.cloud_service_name,
                ctx.deployment_name,
                ctx.virtual_machine_name,
                ctx.endpoint_name)

            if not public_ip:
                self.log.warn("unable to find public ip for vm %s, set guacamole failed" % ctx.virtual_machine_name)
            else:
                remote_para = get_remote_parameters(
                    ctx.raw_system_config,
                    ctx.remote,
                    ctx.virtual_machine_name,
                    public_ip, port)

                ve.remote_paras = json.dumps(remote_para)

            self.db.commit()
            self.expr_manager.check_expr_status(ve.experiment)

        self.log.debug("azure virtual environment %d vm success callback done, step to next" % sctx.current_job_index)
        # step to config next unit
        sctx.current_job_index += 1
        self.__schedule_setup(sctx)
