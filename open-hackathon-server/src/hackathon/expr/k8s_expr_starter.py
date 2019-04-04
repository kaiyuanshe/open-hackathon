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
from hackathon.hk8s.k8s_service_adapter import K8SServiceAdapter
import time

class K8SExprStarter(ExprStarter):

    def _internal_start_expr(self, context):
        try:
            # TODO: context.hackathon may be None when tesing a template before any hackathon bind it
            hackathon = Hackathon.objects.get(id=context.hackathon_id)
            experiment = Experiment.objects.get(id=context.experiment_id)

            self.__start_k8s_service(experiment, hackathon, context)
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return internal_server_error('Failed starting k8s')

    def _internal_stop_expr(self, context):
        try:
            experiment = Experiment.objects.get(id=context.experiment_id)
            template_content = self.template_library.load_template(experiment.template)

            self.__stop_k8s_service(experiment, hackathon, context)
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return internal_server_error('Failed stopping k8s')



    def _internal_rollback(self, context):
        raise NotImplementedError()

    #private functions
    def __start_k8s_service(self, experiment, hackathon, context):

        experiment.virtual_environments.append(VirtualEnvironment(
                provider = VE_PROVIDER.K8S,
                name = hackathon.name,
                #k8s_resource = k8s_dict,
                status = VEStatus.INIT,
                remote_provider = VERemoteProvider.Guacamole))

        # save constructed experiment, and execute from first job content
        experiment.save()
        self.__schedule_start(context)

    def __schedule_start(self, ctx):
        self.scheduler.add_once("k8s_service", "schedule_start_k8s_service", context=ctx,
                                id="schedule_setup_" + str(ctx.experiment_id), seconds=0)

    def __wait_for_k8s_availability(adapter):
        attempts = 10

        while attempts:
            attempts -= 1
            time.sleep(1)
            if adapter.get_deployment_status(name) == K8S_DEPLOYMENT_STATUS.AVAILABLE:
                return True

        return False

    def schedule_start_k8s_service(self, ctx):
        template_unit = context.template_content.units
        name       = ctx.user_id + "_" + template_unit.get_name()
        adapter    = self.__get_adapter_from_ctx(K8SServiceAdapter, ctx)

        if not adapter.deployment_exists(name):
            try:
                ret =  adapter.create_k8s_environment(template_unit)
                #checke deployment's status after sleeping 5 seconds
                if __wait_for_k8s_availability(adapter):
                    self.__on_message("k8s_service_create_completed", ctx)
                else:
                    self.__on_message("k8s_service_create_failed", ctx)
            except Exception as e:
                self.__on_message("k8s_service_create_failed", ctx)

        else:
            if adapter.get_deployment_status(name) != K8S_DEPLOYMENT_STATUS.AVAILABLE:
                try:
                    ret =  adapter.start_k8s_deployment(name)
                    self.__on_message("k8s_service_start_completed", ctx)
                except Exception as e:
                    self.__on_message("k8s_service_start_failed", ctx)


    def __stop_k8s_service(self, experiment, hackathon, context):
        self.__schedule_stop(context)

    def __schedule_stop(self, ctx):
        self.scheduler.add_once("k8s_service", "schedule_stop_k8s_service", context=ctx,
                                id="schedule_stop_" + str(ctx.experiment_id), seconds=0)

    def schedule_stop_k8s_service(self, ctx):
        template_unit = context.template_content.units
        name       = template_unit.get_name()
        adapter    = self.__get_adapter_from_ctx(K8SServiceAdapter, ctx)

        try:
            ret =  adapter.pause_k8s_deployment(name)
            self.__on_message("k8s_service_stop", ctx)
        except Exception as e:
            self.__on_message("k8s_service_stop_failed", ctx)


    def __on_message(self, msg, ctx):
        self.log.debug("k8s on_message: %d" % msg)
        #self.scheduler.add_once(
            #"k8s_service", "__msg_handler",
            #id="k8s_msg_handler_" + str(ctx.experiment_id),
            #context=ctx, seconds=ASYNC_OiP_QUERY_INTERVAL)

    def __msg_handler(msg, ctx):
        switcher = {
            "wait_for_start_k8s_service": "wait_for_start_k8s_service",
            "k8s_service_start_completed":"k8s_service_start_completed",
            "k8s_service_start_failed":"k8s_service_start_failed",
            "wait_for_stop_k8s_service":"wait_for_stop_k8s_service",
            "k8s_service_stop_completed":"k8s_service_stop_completed",
            "k8s_service_stop_failed":"k8s_service_stop_failed",
        }
        msg = switcher.get(item,"nothing")
        #TODO: try to abstract common behavior

    def __get_adapter_from_ctx(self, adapter_class, context):
        template_unit = context.template_content.units
        name       = template_unit.get_name()
        cluster    = template_unit.get_cluster()
        api_url    = cluster[K8S_UNIT.CONFIG_API_SERVER]
        token      = cluster[K8S_UNIT.CONFIG_API_TOKEN]
        namespace  = cluster[K8S_UNIT.CONFIG_NAMESPACES]

        return adapter_class(api_url, token, namespace)
