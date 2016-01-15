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
from hackathon.database import VirtualEnvironment, Experiment
from hackathon.constants import (
    ADStatus, AVMStatus, VEStatus, EStatus)

from cloud_service_adapter import CloudServiceAdapter
from storage_account_adapter import StorageAccountAdapter
from virtual_machine_adapter import VirtualMachineAdapter
from utils import get_network_config, get_remote_parameters
from constants import ASYNC_OP_QUERY_INTERVAL, ASYNC_OP_RESULT, ASYNC_OP_QUERY_INTERVAL_LONG, REMOTE_CREATED_RECORD


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
        ctx = Context(
            job_ctxs=job_ctxs,
            current_job_index=0,
            resource_id=resource_id,

            subscription_id=azure_key.subscription_id,
            pem_url=azure_key.pem_url,
            management_host=azure_key.management_host,

            # remote_created is used to store the resources we create we create remote
            # so we can do rollback
            # TODO: if the user create a virtual machine with vm_image, we have to config the network of it
            #       but so far we have no way to rollback the network settings of it
            remote_created=[])

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
                resource_extension_references=unit.get_resource_extension_references(),
                is_vm_image=unit.is_vm_image(),
                remote=unit.get_remote(),
                endpoint_name=unit.get_remote_port_name(),

                # NOTE: ONLY callback purpose functions can depend on virutal_environment_id
                virtual_environment_id=ve.id,

                # TODO: this part of info should move to super context
                subscription_id=azure_key.subscription_id,
                pem_url=azure_key.pem_url,
                management_host=azure_key.management_host))

        # execute from first job context
        self.__schedule_setup(ctx)

    def stop_vm(self, resource_id, azure_key, template_units, virtual_environments, expr_id):
        """stop the virtual machine, and deallocate the resouces of the virtual machine

        NOTE: virtual_environments and expr_id are just a workaround to update db status, it will be elimated in future
        """
        assert len(template_units) == len(virtual_environments)

        job_ctxs = []
        ctx = Context(job_ctxs=job_ctxs, current_job_index=0, resource_id=resource_id)

        for i in xrange(0, len(template_units)):
            unit = template_units[i]
            ve = virtual_environments[i]

            job_ctxs.append(Context(
                cloud_service_name=unit.get_cloud_service_name(),
                deployment_slot=unit.get_deployment_slot(),
                virtual_machine_name=self.get_virtual_machine_name(unit.get_virtual_machine_name(), resource_id),

                # NOTE: ONLY callback purpose functions can depend on virutal_environment_id and expr id
                virtual_environment_id=ve.id,
                expr_id=expr_id,

                subscription_id=azure_key.subscription_id,
                pem_url=azure_key.pem_url,
                management_host=azure_key.management_host))

        self.__schedule_stop(ctx)

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

        try:
            if not adapter.cloud_service_exists(ctx.cloud_service_name):
                if not adapter.create_cloud_service(
                        name=ctx.cloud_service_name,
                        label=ctx.cloud_service_label,
                        location=ctx.cloud_service_host):
                    self.log.error("azure virtual environment %d create remote cloud service failed via creation" %
                                   sctx.current_job_index)
                    self.__on_setup_failed(sctx)
                    return

                # create the cloud service remote successfully, record
                sctx.remote_created.append(Context(
                    type=REMOTE_CREATED_RECORD.TYPE_CLOUD_SERVICE,
                    name=ctx.cloud_service_name))
        except Exception as e:
            self.log.error(
                "azure virtual environment %d create remote cloud service failed: %r"
                % (sctx.current_job_index, str(e)))
            self.__on_setup_failed(sctx)
            return

        self.log.debug("azure virtual environment %d cloud service setup done" % sctx.current_job_index)

        # next step: setup storage
        self.scheduler.add_once("azure_formation", "setup_storage", context=sctx, seconds=0)
        return

    def setup_storage(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = StorageAccountAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        try:
            if not adapter.storage_account_exists(ctx.storage_account_name):
                # TODO: use the async way
                if not adapter.create_storage_account(
                        ctx.storage_account_name,
                        ctx.storage_account_description,
                        ctx.storage_account_label,
                        ctx.storage_account_location):
                    self.log.error("azure virtual environment %d create storage account failed via creation" %
                                   sctx.current_job_index)
                    self.__on_setup_failed(sctx)
                    return

                # create storage account remote successfully, record
                sctx.remote_created.append(Context(
                    type=REMOTE_CREATED_RECORD.TYPE_STORAGE_ACCOUNT,
                    name=ctx.storage_account_name))
        except Exception as e:
            self.log.error(
                "azure virtual environment %d create storage account failed: %r"
                % (sctx.current_job_index, str(e)))
            self.__on_setup_failed(sctx)
            return

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
                    provision_guest_agent=True,
                    resource_extension_references=ctx.resource_extension_references,
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
                provision_guest_agent=True,
                resource_extension_references=ctx.resource_extension_references,
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
            self.__on_add_virtual_machine_success,
            self.__on_setup_failed,
            self.__wait_for_add_virtual_machine)

    def __on_add_virtual_machine_success(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        # add virtual machine success, record
        sctx.remote_created.append(Context(
            type=REMOTE_CREATED_RECORD.TYPE_ADD_VIRTUAL_MACHINE,
            cloud_service_name=ctx.cloud_service_name,
            deployment_name=ctx.deployment_name,
            virtual_machine_name=ctx.virtual_machine_name))

        self.__wait_for_virtual_machine_ready(sctx)

    def __wait_for_create_virtual_machine_deployment(self, sctx):
        self.log.debug("azure virtual environment: %d, waiting for create vm_deployment" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_formation", "wait_for_create_virtual_machine_deployment",
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_create_virtual_machine_deployment(self, sctx):
        self.__check_vm_operation_status(
            sctx,
            self.__on_create_virtual_machine_deployment_success,
            self.__on_setup_failed,
            self.__wait_for_create_virtual_machine_deployment)

    def __on_create_virtual_machine_deployment_success(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        # create virtual machine deployment success, record
        sctx.remote_created.append(Context(
            type=REMOTE_CREATED_RECORD.TYPE_CREATE_VIRTUAL_MACHINE_DEPLOYMENT,
            cloud_service_name=ctx.cloud_service_name,
            deployment_name=ctx.deployment_name,
            virtual_machine_name=ctx.virtual_machine_name))

        self.__wait_for_deployment_ready(sctx)

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

            # currently we cannot rollback configs, so we don't record here
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
            ctx = sctx.job_ctxs[sctx.current_job_index]
            ve = self.db.find_first_object_by(VirtualEnvironment, id=ctx.virtual_environment_id)

            if ve:
                ve.status = VEStatus.FAILED
                ve.experiment.status = EStatus.FAILED
                self.db.commit()
        finally:
            self.log.debug(
                "azure virtual environment %d vm fail callback done, roll back start"
                % sctx.current_job_index)
            try:
                # rollback reverse
                self.__setup_rollback(sctx.remote_created[::-1], sctx)
                self.log.debug("azure virtual environment %d rollback done" % sctx.current_job_index)
            except Exception as e:
                self.log.error(
                    "azure virtual environment %d error while rollback: %r" %
                    (sctx.current_job_index, str(e)))

    def __setup_rollback(self, record, sctx):
        # TODO: the rollback process should use a async way same
        #       as previous setup process, but for convinence,
        #       we do it in a sync way
        for rec in record:
            if rec.type == REMOTE_CREATED_RECORD.TYPE_CLOUD_SERVICE:
                adapter = CloudServiceAdapter(sctx.subscription_id, sctx.pem_url, host=sctx.management_host)
                adapter.delete_cloud_service(rec.name, complete=True)
            elif rec.type == REMOTE_CREATED_RECORD.TYPE_STORAGE_ACCOUNT:
                adapter = StorageAccountAdapter(sctx.subscription_id, sctx.pem_url, host=sctx.management_host)
                adapter.delete_storage_account(rec.name)
            elif (rec.type == REMOTE_CREATED_RECORD.TYPE_ADD_VIRTUAL_MACHINE
                    or rec.type == REMOTE_CREATED_RECORD.TYPE_CREATE_VIRTUAL_MACHINE_DEPLOYMENT):
                adapter = VirtualMachineAdapter(sctx.subscription_id, sctx.pem_url, host=sctx.management_host)

                if rec.type == REMOTE_CREATED_RECORD.TYPE_ADD_VIRTUAL_MACHINE:
                    adapter.delete_virtual_machine(
                        rec.cloud_service_name,
                        rec.deployment_name,
                        rec.virtual_machine_name,
                        True)
                else:
                    adapter.delete_deployment(
                        rec.cloud_service_name,
                        rec.deployment_name,
                        True)
            else:
                self.log.warn("unknown record type: %s" % rec.type)

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

    def __schedule_stop(self, sctx):
        self.scheduler.add_once("azure_formation", "schedule_stop", context=sctx, seconds=0)

    def schedule_stop(self, sctx):
        current_job_index = sctx.current_job_index
        job_ctxs = sctx.job_ctxs

        if current_job_index >= len(job_ctxs):
            self.log.debug("azure virtual environment stop finish")
            return True

        self.log.debug(
            "azure virtual environment %d: '%r' stop progress begin" %
            (current_job_index, job_ctxs[current_job_index]))
        self.scheduler.add_once("azure_formation", "stop_virtual_machine", context=sctx, seconds=0)

    def stop_virtual_machine(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = VirtualMachineAdapter(ctx.subscription_id, ctx.pem_url, host=ctx.management_host)

        deployment_name = adapter.get_deployment_name(ctx.cloud_service_name, ctx.deployment_slot)
        now_status = adapter.get_virtual_machine_instance_status(
            ctx.cloud_service_name, ctx.deployment_slot, ctx.virtual_machine_name)

        if now_status is None:
            self.log.error(
                "azure virtual environment %d stop vm failed: cannot get status of vm %r" %
                (sctx.current_job_index, ctx.virtual_machine_name))
            self.__on_stop_virtual_machine_failed(sctx)
        elif now_status != AVMStatus.STOPPED_DEALLOCATED:
            try:
                req = adapter.stop_virtual_machine(
                    ctx.cloud_service_name, deployment_name, ctx.virtual_machine_name, AVMStatus.STOPPED_DEALLOCATED)
            except Exception as e:
                self.log.error(
                    "azure virtual environment %d stop vm failed: %r" %
                    (sctx.current_job_index, str(e.message)))
                self.__on_stop_virtual_machine_failed(sctx)
                return False

            ctx.request_id = req.request_id
            self.__wait_for_stop_virtual_machine(sctx)
        else:
            self.__stop_virtual_machine_done(sctx)

    def __wait_for_stop_virtual_machine(self, sctx):
        self.log.debug("azure virtual environment %d, waiting for stop virtual machine" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_formation", "wait_for_stop_virtual_machine", context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_stop_virtual_machine(self, sctx):
        self.__check_vm_operation_status(
            sctx,
            self.__stop_virtual_machine_done,
            self.__on_stop_virtual_machine_failed,
            self.__wait_for_stop_virtual_machine)

    def __on_stop_virtual_machine_failed(self, sctx):
        try:
            self.log.debug("azure virtual environment %d stop vm failed" % sctx.current_job_index)
            # TODO: rollback
        finally:
            self.log.debug(
                "azure virtual environment %d vm setup fail callback done, step to next" % sctx.current_job_index)
            # after rollback done, step into next unit
            sctx.current_job_index += 1
            self.__schedule_stop(sctx)

    def __stop_virtual_machine_done(self, sctx):
        self.log.debug("azure virtual environment %d stop vm done" % sctx.current_job_index)
        ctx = sctx.job_ctxs[sctx.current_job_index]

        # update the status of virtual environment
        ve = self.db.find_first_object_by(VirtualEnvironment, id=ctx.virtual_environment_id)

        if ve:
            ve.status = VEStatus.STOPPED
            self.expr_manager.check_expr_status(ve.experiment)

        # all stopped
        # TODO: alter this as a hook, and trigger this hook in __schedule_stop, where the last job index should be checked
        if sctx.current_job_index == len(sctx.job_ctxs) - 1:
            self.log.debug("resource id: %d all unit stop succeeded!" % sctx.resource_id)
            expr = self.db.find_first_object_by(Experiment, id=ctx.expr_id)
            expr.status = EStatus.STOPPED

        self.db.commit()

        self.log.debug("azure virtual environment %d vm success callback done, step to next" % sctx.current_job_index)
        # step to config next unit
        sctx.current_job_index += 1
        self.__schedule_setup(sctx)
