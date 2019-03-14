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
        config_file = template_unit.get_config()

        ctx = Context(
            current_job_index = 0,
            experiment_id = experiment.id,
            yame_file = yaml,
            deployment_name = deployment,
            config = config_file
            )


        k8s_dict = {"yaml":yaml, "deployment":deployment, "config":config_file}
        experiment.virtual_environments.append(VirtualEnvironment(
                provider = VE_PROVIDER.K8S,
                name = hackathon.name,
                k8s_resource = k8s_dict,
                status = VEStatus.INIT,
                remote_provider = VERemoteProvider.Guacamole))

        # save constructed experiment, and execute from first job content
        experiment.save()
        self.__schedule_start(ctx)

    def __schedule_start(self, ctx):
        self.scheduler.add_once("k8s_service", "__schedule_start_k8s_service", context=ctx,
                                id="schedule_setup_" + str(ctx.experiment_id), seconds=0)

    def __schedule_start_k8s_service(self, ctx):
        adapter = self.__get_adapter_from_ctx(K8SServiceAdapter. ctx.config)
        # create k8s deployment with yaml if it doesn't exist
        if not adapter.deployment_exists(ctx.deployment_name):
            ret = adapter.create_k8s_deployment_with_yaml(ctx.yaml_file, ctx.deployment_name, "default")
            #print ret

        if ret is None:
            self.__on_message("k8s_service_start_failed", ctx)
            return
        # wait for an existing deployment ready and start it
        try:
            # call it in synchronized way and get result immediately
            adapter.start_k8s_service(ctx.deployment_name, "default")
            self.__on_message("k8s_service_start_completed", ctx)
            return
        except Exception as e:
            self.__on_message("k8s_service_start_failed", ctx)


    def __stop_k8s_service(self, experiment, hackathon, template_units):
        self.__schedule_stop(ctx)

    def __schedule_stop(self, ctx):
        self.scheduler.add_once("k8s_service", "__schedule_stop_k8s_service", context=ctx,
                                id="schedule_stop_" + str(ctx.experiment_id), seconds=0)

    def __schedule_stop_k8s_service(self, ctx):
        # get context from super context
        adapter = self.__get_adapter_from_ctx(K8SServiceAdapter, ctx.config)
        # TODO: How to stop an running deployment in k8s
        adapter.stop_k8s_service(ctx.deployment_name)
        self.__on_message("wait_for_stop_k8s_service", ctx)

    def __on_message(self, msg, ctx):
        self.log.debug("k8s on_message: %d" % msg)
        self.scheduler.add_once(
            "k8s_service", "__msg_handler",
            id="k8s_msg_handler_" + str(ctx.experiment_id),
            context=ctx, seconds=ASYNC_OiP_QUERY_INTERVAL)

    def __msg_handler(msg, ctx):
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

    def __get_adapter_from_ctx(self, adapter_class, config):
        return adapter_class(config)
