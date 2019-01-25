# -*- coding: utf-8 -*-
"""
Copyright (c) KaiYuanShe All rights reserved.

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.abs
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.abs"""

__all__ = ["K8SExprStarter"]
import sys

sys.path.append("..")

from expr_starter import ExprStarter
from hackathon import RequiredFeature, Context
from hackathon.hmongo.models import Hackathon, VirtualEnvironment, Experiment, AzureVirtualMachine, AzureEndPoint
from hackathon.constants import (VE_PROVIDER, VERemoteProvider, VEStatus, ADStatus, AVMStatus, EStatus)
from hackathon.hackathon_response import internal_server_error
from hackathon.template.template_constants import AZURE_UNIT
from hackathon.hk8s import K8SServiceAdapter

class K8SExprStarter(ExprStarter):

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
            return internal_server_error('Failed starting k8s')

    def _internal_stop_expr(self, context):
        raise NotImplementedError()

    def _internal_rollback(self, context):
        raise NotImplementedError()

    #private functions
    def __start_vm(self, experiment, hackathon, template_units):
        job_ctxs = []
        ctx = Context(
            job_ctxs=job_ctxs,
            current_job_index=0,
            experiment_id=experiment.id,

            #subscription_id=azure_key.subscription_id,
            #pem_url=azure_key.get_local_pem_url(),
            #management_host=azure_key.management_host
            )


        experiment.virtual_environments.append(VirtualEnvironment(
                provider=VE_PROVIDER.K8S,
                name=vm_name,
                image=unit.get_image_name(),
                status=VEStatus.INIT,
                remote_provider=VERemoteProvider.Guacamole))

        # save constructed experiment, and execute from first job content
        experiment.save()
        self.__schedule_setup(ctx)

    def __schedule_setup(self, sctx):
        self.scheduler.add_once("k8s_service", "schedule_k8s_service", context=sctx,
                                id="schedule_setup_" + str(sctx.experiment_id), seconds=0)

    def setup_k8s_service(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, K8SServiceAdapter)
        # TODO: Implement deployment_exists in K8SServiceAdapter
        if adapter.deployment_exists(ctx.cloud_service_name, ctx.deployment_slot):
            self.__setup_k8s_with_deployment_existed(sctx)
        else:
            self.__setup_k8s_without_deployment_existed(sctx)

    def __setup_k8s_with_deployment_existed(self, sctx):
        # get context from super context
        #ctx = sctx.job_ctxs[sctx.current_job_index]
        #adapter = self.__get_adapter_from_sctx(sctx, K8SServiceAdapter)

        try:
            self.start_k8s_deployment(sctx, name)
            self.__wait_for_start_k8s_service(sctx)
            return
        except Exception as e:
            self.log.error(
                "k8s  %d start a service %r failed: %r"
                % (sctx.current_job_index, ctx.virtual_machine_name, str(e)))
            self._on_setup_k8s_failed(sctx)


    def __setup_k8s_without_deployment_existed(self, sctx):
        #ctx = sctx.job_ctxs[sctx.current_job_index]
        #adapter = self.__get_adapter_from_sctx(sctx, K8SServiceAdapter)
        try:
            self.create_k8s_deployment(sctx, yaml)
            self.__wait_for_create_k8s_service(sctx)
        except Exception as e:
            self.log.error(
                "k8s %d create service %r failed: %r"
                % (sctx.current_job_index, ctx.virtual_machine_name, str(e)))
            self._on_setup_k8s_failed(sctx)

    def __wait_for_create_k8s_service(self, sctx):
        #TODO: check its status
        raise NotImplementedError()

    def __wait_for_start_k8s_service(self, sctx):
        #TODO: check its status
        raise NotImplementedError()

    def _on_setup_k8s_failed(self, sctx):
        try:
            self.log.debug("k8s environment %d vm setup failed" % sctx.current_job_index)
            expr = Experiment.objects(id=sctx.experiment_id).first()
            ve = expr.virtual_environments[sctx.current_job_index]

            ve.status = VEStatus.FAILED
            expr.status = EStatus.FAILED
            expr.save()
        finally:
            self.log.debug(
                "k8s environment %d vm fail callback done, roll back start"
                % sctx.current_job_index)
            # rollback reverse
            self._internal_rollback(sctx)

    def _internal_rollback(self, sctx):
        try:
            #TODO figure out what rollback is and rollback
            self.log.debug("k8s environment %d rollback done" % sctx.current_job_index)
        except Exception as e:
                self.log.error(
                    "k8s environment %d error while rollback: %r" %
                    (sctx.current_job_index, str(e)))

    def create_k8s_deployment(self, sctx,  yaml):
        # TODO: create a k8s service with yaml
        adapter = self.__get_adapter_from_sctx(sctx, K8SServiceAdapter)
        #adapter.xxx()
        raise NotImplementedError()

    def start_k8s_deployment(self, sctx, name):
        adapter = self.__get_adapter_from_sctx(sctx, K8SServiceAdapter)
        #adapter.xxx()
        # TODO: start an existing k8s service
        raise NotImplementedError()

    def stop_k8s_deployment(self, name):
        raise NotImplementedError()

    def __get_adapter_from_sctx(self, sctx, adapter_class):
        return adapter_class()
