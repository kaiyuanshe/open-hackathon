# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
import copy
import time

from expr_starter import ExprStarter
from hackathon.hmongo.models import Hackathon, VirtualEnvironment, Experiment, AzureVirtualMachine, AzureEndPoint
from hackathon.constants import (VE_PROVIDER, VERemoteProvider, VEStatus, ADStatus, AVMStatus, EStatus)
from hackathon.hackathon_response import internal_server_error
from hackathon.constants import K8S_DEPLOYMENT_STATUS
from hackathon.template.template_constants import K8S_UNIT
from hackathon.hk8s.k8s_service_adapter import K8SServiceAdapter


class K8SExprStarter(ExprStarter):
    def _internal_start_expr(self, context):
        hackathon = Hackathon.objects.get(id=context.hackathon_id)
        experiment = Experiment.objects.get(id=context.experiment_id)
        if not experiment or not hackathon:
            return internal_server_error('Failed starting k8s: experiment or hackathon not found.')
        user = experiment.user or None
        _virtual_envs = []
        try:
            if user:
                _virtual_envs = experiment.virtual_environments
            if not _virtual_envs:
                # Get None VirtualEnvironment, create new one:
                for template_unit in context.template_content.units:
                    k8s_dict = self.__create_useful_k8s_dict(hackathon, experiment, template_unit)
                    experiment.virtual_environments.append(VirtualEnvironment(
                        provider=VE_PROVIDER.K8S,
                        name=k8s_dict['name'],
                        k8s_resource=k8s_dict,
                        status=VEStatus.INIT,
                        remote_provider=VERemoteProvider.Guacamole))

                    # save constructed experiment, and execute from first job content
                    experiment.save()
                    self.log.debug("virtual_environments %s created, creating k8s..." % k8s_dict['name'])
                    self.__schedule_create(context)
            else:
                self.__schedule_start(context)
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return internal_server_error('Failed starting k8s')

    def _internal_stop_expr(self, context):
        experiment = Experiment.objects.get(id=context.experiment_id)
        if not experiment:
            return internal_server_error('Failed stop k8s: experiment not found.')
        try:
            context.virtual_environments = experiment.virtual_environments
            self.__schedule_stop(context)

            experiment.delete()
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return internal_server_error('Failed stopping k8s')

    def _internal_rollback(self, context):
        raise NotImplementedError()

    def __schedule_create(self, ctx):
        self.scheduler.add_once("k8s_service", "schedule_create_k8s_service", context=ctx,
                                id="schedule_setup_" + str(ctx.experiment_id), seconds=0)

    def __schedule_start(self, ctx):
        self.scheduler.add_once("k8s_service", "schedule_start_k8s_service", context=ctx,
                                id="schedule_setup_" + str(ctx.experiment_id), seconds=0)

    def __schedule_stop(self, ctx):
        self.scheduler.add_once("k8s_service", "schedule_stop_k8s_service", context=ctx,
                                id="schedule_stop_" + str(ctx.experiment_id), seconds=0)

    def schedule_create_k8s_service(self, context):
        template_unit = context.template_content.units[0]
        experiment = Experiment.objects.get(id=context.experiment_id)
        virtual_env = experiment.virtual_environments[0]
        k8s_dict = virtual_env.k8s_resource
        adapter = self.__get_adapter_from_ctx(K8SServiceAdapter, context)

        template_unit.set_ports(k8s_dict['ports'])
        labels = {
            "template_name": context.template_name,
            "hackathon_id": context.hackathon_id,
            "experiment_id": context.experiment_id,
        }
        try:
            deploy_name, port = adapter.create_k8s_environment(virtual_env.name, template_unit, labels=labels)

            expr = Experiment.objects(id=context.experiment_id).first()
            virtual_env = expr.virtual_environments[0]
            k8s_dict = virtual_env.k8s_resource
            vnc_port = k8s_dict['ports']
            vnc_port[0][K8S_UNIT.PORTS_PUBLIC_PORT] = port
            expr.save()

            # check deployment's status
            if self.__wait_for_k8s_status(adapter, virtual_env.name, K8S_DEPLOYMENT_STATUS.AVAILABLE):
                self.log.debug("k8s deployment succeeds: %s" % str(context))
                self.__on_create_success(context)
            else:
                self.log.error("k8s deployment fails: %s" % str(context))
                self.__on_message("k8s_service_create_failed", context)
        except Exception as e:
            self.__on_message("k8s_service_create_failed", context)

    def schedule_start_k8s_service(self, context):
        experiment = Experiment.objects.get(id=context.experiment_id)
        virtual_env = experiment.virtual_environments[0]
        adapter = self.__get_adapter_from_ctx(K8SServiceAdapter, context)

        try:
            if adapter.get_deployment_status(virtual_env.name) != K8S_DEPLOYMENT_STATUS.PAUSE:
                raise RuntimeError("K8s Service not has paused")

            adapter.start_k8s_deployment(virtual_env.name)
            if self.__wait_for_k8s_status(adapter, virtual_env.name, K8S_DEPLOYMENT_STATUS.AVAILABLE):
                self.__on_message("k8s_service_start_sucess", context)
            else:
                self.__on_message("k8s_service_start_failed", context)
        except Exception as e:
            self.__on_message("k8s_service_start_failed", context)

    def schedule_stop_k8s_service(self, context):
        virtual_envs = context.virtual_environments
        try:
            adapter = self.__get_adapter_from_ctx(K8SServiceAdapter, context)
            for virtual_env in virtual_envs:
                if adapter.get_deployment_status(virtual_env.name) == K8S_DEPLOYMENT_STATUS.PAUSE:
                    continue
                adapter.pause_k8s_deployment(virtual_env.name)
            self.__on_message("k8s_service_stop", context)
        except Exception as e:
            self.__on_message("k8s_service_stop_failed", context)

    def __on_message(self, msg, ctx):
        self.log.debug("k8s on_message: {}".format(msg))
        # self.scheduler.add_once(
        # "k8s_service", "__msg_handler",
        # id="k8s_msg_handler_" + str(ctx.experiment_id),
        # context=ctx, seconds=ASYNC_OiP_QUERY_INTERVAL)

    def __msg_handler(msg, ctx):
        switcher = {
            "wait_for_start_k8s_service": "wait_for_start_k8s_service",
            "k8s_service_start_completed": "k8s_service_start_completed",
            "k8s_service_start_failed": "k8s_service_start_failed",
            "wait_for_stop_k8s_service": "wait_for_stop_k8s_service",
            "k8s_service_stop_completed": "k8s_service_stop_completed",
            "k8s_service_stop_failed": "k8s_service_stop_failed",
        }
        msg = switcher.get(item, "nothing")
        # TODO: try to abstract common behavior

    @staticmethod
    def __create_useful_k8s_dict(hackathon, experiment, template_unit):
        # FIXME K8s dict need a db model, not a dict
        _experiments = Experiment.objects(hackathon=hackathon).all()
        _virtual_envs = []
        for e in _experiments:
            _virtual_envs += list(e.virtual_environments)

        # TODO Need to check the rules about K8s resource name
        _names = [v.name for v in _virtual_envs]
        count = 0
        name = None
        while count < 100:
            count += 1
            name = "{}-{}-{}".format(template_unit.name, experiment.id, count)
            if name not in _names:
                break
        if count >= 100:
            raise RuntimeError("Can't get useful env name.")

        # Ensure that the external ports do not conflict
        ports = copy.deepcopy(template_unit.get_ports())
        return {
            "name": "{}".format(name).lower(),
            "ports": ports,
        }

    def __wait_for_k8s_status(self, adapter, service_name, status):
        attempts = 30

        while attempts:
            self.log.debug("__wait_for_k8s_status, service_name: %s, target status: %d, remaining attempts: %d"
                           % (service_name, status, attempts))
            attempts -= 1
            time.sleep(10)
            if adapter.get_deployment_status(service_name) == status:
                return True
        return False

    @staticmethod
    def __get_adapter_from_ctx(adapter_class, context):
        template_unit = context.template_content.units[0]
        cluster = template_unit.get_cluster()
        api_url = cluster[K8S_UNIT.CONFIG_API_SERVER]
        token = cluster[K8S_UNIT.CONFIG_API_TOKEN]
        namespace = cluster[K8S_UNIT.CONFIG_NAMESPACES]
        return adapter_class(api_url, token, namespace)

    def __on_create_success(self, context):
        self.log.debug("experiment started %s successfully. Setting remote parameters." % context.experiment_id)
        # set experiment status
        # update the status of virtual environment
        expr = Experiment.objects(id=context.experiment_id).first()
        virtual_env = expr.virtual_environments[0]

        # guacamole parameters
        k8s_dict = virtual_env.k8s_resource
        # TODO need to choose right port/protocol based on template
        vnc_port = k8s_dict['ports']
        if len(vnc_port):
            gc = {
                K8S_UNIT.REMOTE_PARAMETER_NAME: virtual_env.name,
                K8S_UNIT.REMOTE_PARAMETER_DISPLAY_NAME: vnc_port[0][K8S_UNIT.PORTS_NAME],
                # TODO need to query K8S list all supported IPs and pick one randomly either here or connecting phase
                # K8S_UNIT.REMOTE_PARAMETER_HOST_NAME: "49.4.90.39",
                K8S_UNIT.REMOTE_PARAMETER_PROTOCOL: "vnc",
                K8S_UNIT.REMOTE_PARAMETER_PORT: vnc_port[0][K8S_UNIT.PORTS_PUBLIC_PORT],
                # K8S_UNIT.REMOTE_PARAMETER_USER_NAME: "",
                # K8S_UNIT.REMOTE_PARAMETER_PASSWORD: "",
            }
            self.log.debug("expriment %s remote parameters: %s" % (expr.id, str(gc)))
            virtual_env.remote_paras = gc

        virtual_env.status = VEStatus.RUNNING
        expr.status = EStatus.RUNNING
        expr.save()
