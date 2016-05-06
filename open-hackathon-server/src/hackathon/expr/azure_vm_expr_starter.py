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
__all__ = ["AzureVMExprStarter"]
import sys

sys.path.append("..")

from expr_starter import ExprStarter
from hackathon import RequiredFeature, Context
from hackathon.hmongo.models import Hackathon, VirtualEnvironment, Experiment, AzureVirtualMachine, AzureEndPoint
from hackathon.constants import (
    VE_PROVIDER, VERemoteProvider, VEStatus, ADStatus, AVMStatus, EStatus)
from hackathon.hackathon_response import internal_server_error
from hackathon.template.template_constants import AZURE_UNIT

from hackathon.hazure import CloudServiceAdapter, StorageAccountAdapter, VirtualMachineAdapter
from hackathon.hazure.utils import get_network_config, get_remote_parameters
from hackathon.hazure.constants import (
    ASYNC_OP_QUERY_INTERVAL, ASYNC_OP_RESULT, ASYNC_OP_QUERY_INTERVAL_LONG, REMOTE_CREATED_RECORD)


class AzureVMExprStarter(ExprStarter):
    azure_cert_manager = RequiredFeature("azure_cert_manager")

    def _internal_start_expr(self, context):
        try:
            # TODO: context.hackathon may be None when tesing a template before any hackathon bind it
            hackathon = Hackathon.objects.get(id=context.hackathon_id)
            experiment = Experiment.objects.get(id=context.experiment_id)

            self.__start_vm(experiment, hackathon, context.template_content.units)
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return internal_server_error('Failed starting azure vm')

    def _internal_stop_expr(self, context):
        try:
            experiment = Experiment.objects.get(id=context.experiment_id)
            template_content = self.template_library.load_template(experiment.template)
            azure_key = experiment.azure_key

            self.__stop_vm(experiment, azure_key, template_content.units)
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return internal_server_error('Failed stopping azure')

    # private functions
    def __start_vm(self, experiment, hackathon, template_units):
        azure_keys = hackathon.azure_keys
        # TODO: which key to use?
        azure_key = azure_keys[0]
        experiment.azure_key = azure_key

        # job context
        job_ctxs = []
        ctx = Context(
            job_ctxs=job_ctxs,
            current_job_index=0,

            subscription_id=azure_key.subscription_id,
            pem_url=azure_key.get_local_pem_url(),
            management_host=azure_key.management_host,

            experiment_id=experiment.id,

            # remote_created is used to store the resources we create we create remote
            # so we can do rollback
            # TODO: if the user create a virtual machine with vm_image, we have to config the network of it
            #       but so far we have no way to rollback the network settings of it
            remote_created=[])

        # create virtual environments for units
        # and setup setup job contenxt
        # the setup of each unit must be SERLIALLY EXECUTED
        # to avoid the creation of same resource in same time
        # TODO: we still have't avoid the parrallel excution of the setup of same template
        for i in xrange(len(template_units)):
            unit = template_units[i]
            vm_name = self.__get_virtual_machine_name(unit.get_virtual_machine_name(), experiment.id)

            # set up virtual environment
            experiment.virtual_environments.append(VirtualEnvironment(
                provider=VE_PROVIDER.AZURE,
                name=vm_name,
                image=unit.get_image_name(),
                status=VEStatus.INIT,
                remote_provider=VERemoteProvider.Guacamole))

            # construct job context
            job_ctxs.append(self.__construct_setup_job_context(unit, azure_key, vm_name))

        # save constructed experiment, and execute from first job content
        experiment.save()
        self.__schedule_setup(ctx)

    def __construct_setup_job_context(self, unit, azure_key, vm_name):
        # construct current virtual environment's context
        return Context(
            cloud_service_name=self.__get_cloud_service_name(unit.get_cloud_service_name(),
                                                             azure_key.subscription_id),
            cloud_service_label=unit.get_cloud_service_label(),
            cloud_service_host=unit.get_cloud_service_location(),

            storage_account_name=unit.get_storage_account_name(),
            storage_account_description=unit.get_storage_account_description(),
            storage_account_label=unit.get_storage_account_label(),
            storage_account_location=unit.get_storage_account_location(),

            virtual_machine_name=vm_name,
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
            remote_endpoint_name=unit.get_remote_port_name())

    def __stop_vm(self, experiment, azure_key, template_units):
        job_ctxs = []
        ctx = Context(
            job_ctxs=job_ctxs,
            current_job_index=0,
            experiment_id=experiment.id,

            subscription_id=azure_key.subscription_id,
            pem_url=azure_key.get_local_pem_url(),
            management_host=azure_key.management_host)

        for i in xrange(0, len(template_units)):
            unit = template_units[i]

            job_ctxs.append(Context(
                cloud_service_name=self.__get_cloud_service_name(
                    unit.get_cloud_service_name(),
                    azure_key.subscription_id),
                deployment_slot=unit.get_deployment_slot(),
                virtual_machine_name=self.__get_virtual_machine_name(unit.get_virtual_machine_name(), experiment.id)))

        self.__schedule_stop(ctx)

    def __get_virtual_machine_name(self, virtual_machine_base_name, experiment_id):
        """retrieve the virtual machine name by experiment_id

        experiment_id is used by azure_vm.setup
        """
        return "%s-%s" % (virtual_machine_base_name, str(experiment_id))

    def __get_cloud_service_name(self, raw_cloud_service_name, subscription_id):
        """generate new cloud service name to avoid conflict

        cloud service name conflicts while the same template are used in several subscriptions
        """
        return "%s-%s" % (raw_cloud_service_name, subscription_id[:8])

    def __get_adapter_from_sctx(self, sctx, adapter_class):
        return adapter_class(sctx.subscription_id, sctx.pem_url, host=sctx.management_host)

    def __schedule_setup(self, sctx):
        self.scheduler.add_once("azure_vm", "schedule_setup", context=sctx,
                                id="schedule_setup_" + str(sctx.experiment_id), seconds=0)

    def schedule_setup(self, ctx):
        current_job_index = ctx.current_job_index
        job_ctxs = ctx.job_ctxs

        if current_job_index >= len(job_ctxs):
            self.log.debug("azure virtual environment setup finish")
            return True

        # excute current setup from setup cloud service
        # whole stage:
        #   setup_cloud_service -> setup_storage -> setup_virtual_machine ->(index + 1) schedule_setup
        # on whatever stage when error occurs, will turn into _on_virtual_environment_failed
        self.log.debug(
            "azure virtual environment %d: '%r' setup progress begin" %
            (current_job_index, job_ctxs[current_job_index]))
        self.scheduler.add_once("azure_vm", "setup_cloud_service",
                                id="setup_cloud_service_" + str(ctx.experiment_id),
                                context=ctx, seconds=0)

    def setup_cloud_service(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, CloudServiceAdapter)

        try:
            if not adapter.cloud_service_exists(ctx.cloud_service_name):
                if not adapter.create_cloud_service(
                        name=ctx.cloud_service_name,
                        label=ctx.cloud_service_label,
                        location=ctx.cloud_service_host):
                    self.log.error("azure virtual environment %d create remote cloud service failed via creation" %
                                   sctx.current_job_index)
                    self._on_virtual_environment_failed(sctx)
                    return

                # create the cloud service remote successfully, record
                sctx.remote_created.append(Context(
                    type=REMOTE_CREATED_RECORD.TYPE_CLOUD_SERVICE,
                    name=ctx.cloud_service_name))

            self.log.debug("azure virtual environment %d cloud service setup done" % sctx.current_job_index)
            # next step: setup storage
            self.scheduler.add_once("azure_vm", "setup_storage", id="setup_storage_" + str(sctx.experiment_id),
                                    context=sctx, seconds=0)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d create remote cloud service failed: %r"
                % (sctx.current_job_index, str(e)))
            self._on_virtual_environment_failed(sctx)

    def setup_storage(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, StorageAccountAdapter)

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
                    self._on_virtual_environment_failed(sctx)
                    return

                # create storage account remote successfully, record
                sctx.remote_created.append(Context(
                    type=REMOTE_CREATED_RECORD.TYPE_STORAGE_ACCOUNT,
                    name=ctx.storage_account_name))

            self.log.debug("azure virtual environment %d storage setup done" % sctx.current_job_index)

            # next step: setup virtual machine
            self.scheduler.add_once("azure_vm", "setup_virtual_machine",
                                    id="setup_virtual_machine_" + str(sctx.experiment_id), context=sctx, seconds=0)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d create storage account failed: %r"
                % (sctx.current_job_index, str(e)))
            self._on_virtual_environment_failed(sctx)

    def setup_virtual_machine(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

        if adapter.deployment_exists(ctx.cloud_service_name, ctx.deployment_slot):
            self.__setup_virtual_machine_with_deployment_existed(sctx)
        else:
            self.__setup_virtual_machine_without_deployment_existed(sctx)

    def __setup_virtual_machine_with_deployment_existed(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

        # add virtual machine to deployment
        try:
            deployment_name = adapter.get_deployment_name(ctx.cloud_service_name, ctx.deployment_slot)
            if not ctx.is_vm_image:
                network_config = get_network_config(
                    ctx.raw_network_config,
                    adapter.get_assigned_endpoints(ctx.cloud_service_name))
            else:
                network_config = None

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

                # wait for add virtual machine to finish
                ctx.request_id = req.request_id
                ctx.vm_need_config = True if ctx.is_vm_image else False
                self.__wait_for_add_virtual_machine(sctx)
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
            self._on_virtual_environment_failed(sctx)

    def __setup_virtual_machine_without_deployment_existed(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

        try:
            if not ctx.is_vm_image:
                network_config = get_network_config(
                    ctx.raw_network_config,
                    adapter.get_assigned_endpoints(ctx.cloud_service_name))
            else:
                network_config = None

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
            # wait for add virtual machine to finish
            ctx.request_id = req.request_id
            ctx.vm_need_config = True if ctx.is_vm_image else False
            self.__wait_for_create_virtual_machine_deployment(sctx)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d create virtual machine %r failed: %r"
                % (sctx.current_job_index, ctx.virtual_machine_name, str(e)))
            self._on_virtual_environment_failed(sctx)

    def __check_vm_operation_status(self, sctx, on_success, on_failed, on_continue):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

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
            "azure_vm", "wait_for_add_virtual_machine",
            id="wait_for_add_virtual_machine_" + str(sctx.experiment_id),
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_add_virtual_machine(self, sctx):
        self.__check_vm_operation_status(
            sctx,
            self.__on_add_virtual_machine_success,
            self._on_virtual_environment_failed,
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
            "azure_vm", "wait_for_create_virtual_machine_deployment",
            id="wait_for_create_virtual_machine_deployment_" + str(sctx.experiment_id),
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_create_virtual_machine_deployment(self, sctx):
        self.__check_vm_operation_status(
            sctx,
            self.__on_create_virtual_machine_deployment_success,
            self._on_virtual_environment_failed,
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
        adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

        try:
            network_config = get_network_config(
                ctx.raw_network_config,
                adapter.get_assigned_endpoints(ctx.cloud_service_name))

            if len(network_config.input_endpoints.input_endpoints) == 0:
                # don't need to config, skip
                self.__setup_virtual_machine_done(sctx)
                return

            req = adapter.update_virtual_machine_network_config(
                ctx.cloud_service_name,
                ctx.deployment_name,
                ctx.virtual_machine_name,
                network_config)

            ctx.request_id = req.request_id
            self.__wait_for_config_virtual_machine(sctx)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d error while config network: %r" %
                (sctx.current_job_index, e.message))
            self._on_virtual_environment_failed(sctx)

    def __wait_for_config_virtual_machine(self, sctx):
        self.log.debug("azure virtual environment: %d, waiting for configure network" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_vm", "wait_for_config_virtual_machine",
            id="wait_for_config_virtual_machine_" + str(sctx.experiment_id),
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_config_virtual_machine(self, sctx):
        self.__check_vm_operation_status(
            sctx,

            # currently we cannot rollback configs, so we don't record here
            self.__wait_for_virtual_machine_ready,
            self._on_virtual_environment_failed,
            self.__wait_for_config_virtual_machine)

    def __wait_for_deployment_ready(self, sctx):
        self.log.debug("azure virtual environment: %d, waiting for deployment ready" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_vm", "wait_for_deployment_ready", id="wait_for_deployment_ready_" + str(sctx.experiment_id),
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

    def wait_for_deployment_ready(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

        try:
            props = adapter.get_deployment_by_slot(ctx.cloud_service_name, ctx.deployment_slot)

            if not props:
                self.log.error(
                    "azure virtual environment %d error occured while waiting for deployment ready"
                    % sctx.current_job_index)
                self._on_virtual_environment_failed(sctx)
                return

            if props.status == ADStatus.RUNNING:
                self.__wait_for_virtual_machine_ready(sctx)
            else:
                self.__wait_for_create_virtual_machine_deployment(sctx)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d error while waiting for deployment: %r" %
                (sctx.current_job_index, e.message))
            self._on_virtual_environment_failed(sctx)

    def __wait_for_virtual_machine_ready(self, sctx):
        self.log.debug("azure virtual environment: %d, waiting for vm ready" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_vm", "wait_for_virtual_machine_ready",
            id="wait_for_virtual_machine_ready_" + str(sctx.experiment_id),
            context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL_LONG)

    def wait_for_virtual_machine_ready(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

        try:
            status = adapter.get_virtual_machine_instance_status(
                ctx.cloud_service_name, ctx.deployment_slot, ctx.virtual_machine_name)

            if not status:
                self.log.error(
                    "azure virtual environment %d error occured while waiting for virtual machine ready"
                    % sctx.current_job_index)
                self._on_virtual_environment_failed(sctx)
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
        except Exception as e:
            self.log.error(
                "azure virtual environment %d error while waiting for vm readt: %r" %
                (sctx.current_job_index, e.message))
            self._on_virtual_environment_failed(sctx)

    # callbacks will be called here
    def _on_virtual_environment_failed(self, sctx):
        try:
            self.log.debug("azure virtual environment %d vm setup failed" % sctx.current_job_index)
            expr = Experiment.objects(id=sctx.experiment_id).first()
            ve = expr.virtual_environments[sctx.current_job_index]

            ve.status = VEStatus.FAILED
            expr.status = EStatus.FAILED
            expr.save()
        finally:
            self.log.debug(
                "azure virtual environment %d vm fail callback done, roll back start"
                % sctx.current_job_index)
            # rollback reverse
            self._internal_rollback(sctx)

    def _internal_rollback(self, sctx):
        try:
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
                adapter = self.__get_adapter_from_sctx(sctx, CloudServiceAdapter)
                adapter.delete_cloud_service(rec.name, complete=True)
            elif rec.type == REMOTE_CREATED_RECORD.TYPE_STORAGE_ACCOUNT:
                adapter = self.__get_adapter_from_sctx(sctx, StorageAccountAdapter)
                adapter.delete_storage_account(rec.name)
            elif (rec.type == REMOTE_CREATED_RECORD.TYPE_ADD_VIRTUAL_MACHINE
                  or rec.type == REMOTE_CREATED_RECORD.TYPE_CREATE_VIRTUAL_MACHINE_DEPLOYMENT):
                adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

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
        try:
            self.log.debug("azure virtual environment %d vm setup done" % sctx.current_job_index)
            ctx = sctx.job_ctxs[sctx.current_job_index]

            # update the status of virtual environment
            expr = Experiment.objects(id=sctx.experiment_id).first()
            ve = expr.virtual_environments[sctx.current_job_index]
            adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

            ve.status = VEStatus.RUNNING
            expr.save()

            self._on_virtual_environment_success(Context(
                experiment_id=expr.id))

            azure_resource = AzureVirtualMachine(name=ctx.virtual_machine_name,
                                                 label=ctx.virtual_machine_label,
                                                 dns="%s.chinacloudapp.cn" % ctx.cloud_service_name,
                                                 end_points=[])
            # todo record AzureDeployment, AzureCloudService and so on in db for roll back

            vm_role = adapter.get_virtual_machine_role(ctx.cloud_service_name,
                                                       ctx.deployment_name,
                                                       ctx.virtual_machine_name)

            if (not vm_role) or (not vm_role.instance_endpoints):
                self.log.warn(
                    "unable to find vm %s, cannot update virtual env config like guacamole" % ctx.virtual_machine_name)
            else:
                for endpoint in vm_role.instance_endpoints:
                    azure_resource.public_ip = endpoint.vip
                    if endpoint.name == ctx.remote_endpoint_name:  # endpoint for remote desktop
                        ve.remote_provider = VERemoteProvider.Guacamole
                        ve.remote_paras = get_remote_parameters(
                            ctx.raw_system_config,
                            ctx.remote,
                            ctx.virtual_machine_name,
                            endpoint.vip,
                            endpoint.public_port)
                    else:
                        try:
                            aep = self.__get_persistable_endpoint(endpoint, ctx.raw_network_config)
                            azure_resource.end_points.append(aep)
                        except Exception as e:
                            self.log.error(e)

            ve.azure_resource = azure_resource
            azure_resource.save()
            expr.save()

            self.log.debug(
                "azure virtual environment %d vm success callback done, step to next" % sctx.current_job_index)
            # step to config next unit
            sctx.current_job_index += 1
            self.__schedule_setup(sctx)
        except Exception as e:
            self.log.error("azure virtual environment %d failed on vm_done: %r" % (sctx.current_job_index, e.message))
            self._on_virtual_environment_failed(sctx)

    def __get_persistable_endpoint(self, endpoint, raw_network_config):
        aep = AzureEndPoint(name=endpoint.name,
                            protocol=endpoint.protocol,
                            public_port=int(endpoint.public_port),
                            private_port=(endpoint.local_port))
        raw_ep = filter(lambda r: r[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_NAME] == endpoint.name,
                        raw_network_config[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS])
        if len(raw_ep) > 0:
            aep.url = raw_ep[0].get(AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_URL, None)
        return aep

    def __schedule_stop(self, sctx):
        self.scheduler.add_once("azure_vm", "schedule_stop", context=sctx, seconds=0)

    def schedule_stop(self, sctx):
        current_job_index = sctx.current_job_index
        job_ctxs = sctx.job_ctxs

        if current_job_index >= len(job_ctxs):
            self.log.debug("azure virtual environment stop finish")
            return True

        self.log.debug(
            "azure virtual environment %d: '%r' stop progress begin" %
            (current_job_index, job_ctxs[current_job_index]))
        self.scheduler.add_once("azure_vm", "stop_virtual_machine",
                                id="stop_virtual_machine_" + str(sctx.experiment_id), context=sctx, seconds=0)

    def stop_virtual_machine(self, sctx):
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, VirtualMachineAdapter)

        try:
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
        except Exception as e:
            self.log.error(
                "azure virtual environment %d error while stopping vm: %r" %
                (sctx.current_job_index, e.message))
            self.__on_stop_virtual_machine_failed(sctx)

    def __wait_for_stop_virtual_machine(self, sctx):
        self.log.debug("azure virtual environment %d, waiting for stop virtual machine" % sctx.current_job_index)
        self.scheduler.add_once(
            "azure_vm", "wait_for_stop_virtual_machine",
            id="wait_for_stop_virtual_machine_" + str(sctx.experiment_id), context=sctx, seconds=ASYNC_OP_QUERY_INTERVAL)

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

        try:
            # update the status of virtual environment
            expr = Experiment.objects(id=sctx.experiment_id).first()
            ve = expr.virtual_environments[sctx.current_job_index]

            self._on_virtual_environment_stopped(Context(
                experiment_id=expr.id,
                virtual_environment_name=ve.name))

            self.log.debug("azure virtual environment %d vm success callback done, step to next" % sctx.current_job_index)
            # step to config next unit
            sctx.current_job_index += 1
            self.__schedule_setup(sctx)
        except Exception as e:
            self.log.error(
                "azure virtual environment %d error while stopping vm: %r" %
                (sctx.current_job_index, e.message))
            self.__on_stop_virtual_machine_failed(sctx)
