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
from hackathon.template.template_constants import K8S_UNIT
from hackathon.hk8s import K8SServiceAdapter

class K8SExprStarter(ExprStarter):

    def _internal_start_expr(self, context):
        try:
            # TODO: context.hackathon may be None when tesing a template before any hackathon bind it
            hackathon = Hackathon.objects.get(id=context.hackathon_id)
            experiment = Experiment.objects.get(id=context.experiment_id)

            self.__start_k8s_service(experiment, hackathon, context.template_content.units)
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return internal_server_error('Failed starting k8s')

    def _internal_stop_expr(self, context):
        try:
            experiment = Experiment.objects.get(id=context.experiment_id)
            template_content = self.template_library.load_template(experiment.template)

            self.__stop_k8s_service(experiment, hackathon, context.template_content.units)
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return internal_server_error('Failed stopping k8s')



    def _internal_rollback(self, context):
        raise NotImplementedError()

    #private functions
    def __start_k8s_service(self, experiment, hackathon, template_unit):
        yaml = template_unit.get_yaml_file()
        deployment = template_unit.get_deployment_name()

        ctx = Context(
            current_job_index = 0,
            experiment_id = experiment.id,
            yame_file = yaml,
            deployment_name = deployment
            )


        k8s_dict = {"yaml":yaml, "deployment":deployment}
        experiment.virtual_environments.append(VirtualEnvironment(
                provider = VE_PROVIDER.K8S,
                name = hackathon.name,
                k8s_resource = k8s_dict,
                status = VEStatus.INIT,
                remote_provider = VERemoteProvider.Guacamole))

        # save constructed experiment, and execute from first job content
        experiment.save()
        self.__schedule_start(ctx)

    def __schedule_start(self, sctx):
        self.scheduler.add_once("k8s_service", "__schedule_start_k8s_service", context=sctx,
                                id="schedule_setup_" + str(sctx.experiment_id), seconds=0)

    def __schedule_start_k8s_service(self, sctx):
        adapter = self.__get_adapter_from_sctx(K8SServiceAdapter)
        # create k8s deployment with yaml if it doesn't exist
        if not adapter.deployment_exists(ctx.deployment_name):
            ret = adapter.create_k8s_deployment_with_yaml(ctx.yaml_file, ctx.deployment_name, "default")
            #print ret

        if ret is None:
            self.__on_message("k8s_service_start_failed", sctx)
            return
        # wait for an existing deployment ready and start it
        try:
            # call it in synchronized way and get result immediately
            adapter.start_k8s_service(ctx.cloud.service_name, "default")
            self.__on_message("k8s_service_start_completed", sctx)
            return
        except Exception as e:
            self.__on_message("k8s_service_start_failed", sctx)
            #self.log.error(
            #    "k8s  %d start a service %r failed: %r"
            #    % (sctx.current_job_index, ctx.virtual_machine_name, str(e)))


    def __stop_k8s_service(self, experiment, hackathon, template_units):
        self.__schedule_stop(ctx)

    def __schedule_stop(self, sctx):
        self.scheduler.add_once("k8s_service", "__schedule_stop_k8s_service", context=sctx,
                                id="schedule_stop_" + str(sctx.experiment_id), seconds=0)

    def __schedule_stop_k8s_service(self, sctx):
        # get context from super context
        #ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(K8SServiceAdapter)
        # TODO: How to stop an running deployment in k8s
        adapter.stop_k8s_service(sctx.deployment_name)
        self.__on_message("wait_for_stop_k8s_service", sctx)

    def __on_message(self, msg, sctx):
        self.log.debug("k8s on_message: %d" % msg)
        self.scheduler.add_once(
            "k8s_service", "__msg_handler",
            id="k8s_msg_handler_" + str(sctx.experiment_id),
            context=sctx, seconds=ASYNC_OiP_QUERY_INTERVAL)

    def __msg_handler(msg, sctx):
        switcher = {
            "wait_for_start_k8s_service": "aaaaa",
            "k8s_service_start_completed":"aaaaa",
            "k8s_service_start_failed":"aaaaa",
            "wait_for_stop_k8s_service":"aaaaa",
            "k8s_service_stop_completed":"aaaaa",
            "k8s_service_stop_failed":"aaaaa",
        }
        msg = switcher.get(item,"nothing")
        #TODO: try to abstract common behavior

    def __get_adapter_from_sctx(self, adapter_class):
        return adapter_class()
