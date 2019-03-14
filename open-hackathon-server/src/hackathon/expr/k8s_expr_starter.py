# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

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
    def __start_k8s_service(self, experiment, hackathon, template_units):
        job_ctxs = []
        ctx = context(
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
        self.__schedule_start(ctx)

    def __schedule_start(self, sctx):
        self.scheduler.add_once("k8s_service", "__schedule_start_k8s_service", context=sctx,
                                id="schedule_setup_" + str(sctx.experiment_id), seconds=0)

    def __schedule_start_k8s_service(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, K8SServiceAdapter)
        # create k8s deployment with yaml if it doesn't exist
        if not adapter.deployment_exists(ctx.cloud_service_name):
            status = adapter.create_k8s_deployment_with_yaml(yaml, ctx.cloud_service_name, "default")

        if status != "200":
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
        ctx = sctx.job_ctxs[sctx.current_job_index]
        adapter = self.__get_adapter_from_sctx(sctx, K8SServiceAdapter)
        # TODO: How to stop an running deployment in k8s
        adapter.stop_k8s_service(name)
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

    def __get_adapter_from_sctx(self, sctx, adapter_class):
        return adapter_class()
