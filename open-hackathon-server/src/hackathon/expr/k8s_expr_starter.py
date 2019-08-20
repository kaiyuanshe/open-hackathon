# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
import copy
import time
import string
import random

from expr_starter import ExprStarter
from hackathon.hmongo.models import Hackathon, VirtualEnvironment, Experiment, K8sEnvironment
from hackathon.constants import (VE_PROVIDER, VERemoteProvider, VEStatus, EStatus)
from hackathon.hackathon_response import internal_server_error
from hackathon.constants import K8S_DEPLOYMENT_STATUS
from hackathon.template.template_constants import K8S_UNIT
from hackathon.hk8s.k8s_service_adapter import K8SServiceAdapter


class K8SExprStarter(ExprStarter):
    def _internal_start_expr(self, context):
        hackathon = Hackathon.objects.get(id=context.hackathon_id)
        experiment = Experiment.objects.get(id=context.experiment_id)
        template_content = context.template_content

        if not experiment or not hackathon:
            return internal_server_error('Failed starting k8s: experiment or hackathon not found.')

        user = experiment.user or None
        _virtual_envs = []
        _env_name = str(hackathon.name + "-" + template_content.name).lower()
        if user:
            _virtual_envs = experiment.virtual_environments
            _env_name += str("-" + user.name).lower()

        try:
            if not _virtual_envs:
                # Get None VirtualEnvironment, create new one:
                k8s_env = self.__create_useful_k8s_resource(hackathon, _env_name, template_content)

                experiment.virtual_environments.append(VirtualEnvironment(
                    provider=VE_PROVIDER.K8S,
                    name=_env_name,
                    k8s_resource=k8s_env,
                    status=VEStatus.INIT,
                    remote_provider=VERemoteProvider.Guacamole))

                self.log.debug("virtual_environments %s created, creating k8s..." % _env_name)
                self.__schedule_create(context)
            else:
                self.__schedule_start(context)
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return False

        return True

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
        self.__schedule_stop(context)

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
        experiment = Experiment.objects.get(id=context.experiment_id)
        virtual_env = experiment.virtual_environments[0]
        k8s_resource = virtual_env.k8s_resource
        adapter = self.__get_adapter_from_ctx(K8SServiceAdapter, context)

        labels = {
            "template_name": context.template_name,
            "hackathon_id": context.hackathon_id,
            "experiment_id": context.experiment_id,
        }
        try:
            for s_yaml in k8s_resource.services:
                metadata = s_yaml['metadata']
                metadata['name'] = "{}-{}".format(k8s_resource.name, metadata['name'])
                labels.update(metadata.get("labels") or {})
                metadata['labels'] = labels
                svc_name = adapter.create_k8s_service(s_yaml)
                s_yaml.update(adapter.get_service_by_name(svc_name))

            for d_yaml in k8s_resource.deployments:
                metadata = d_yaml['metadata']
                metadata['name'] = "{}-{}".format(k8s_resource.name, metadata['name'])
                labels.update(metadata.get("labels") or {})
                metadata['labels'] = labels
                adapter.create_k8s_deployment(d_yaml)

            expr = Experiment.objects(id=context.experiment_id).first()
            expr.save()

            # check deployment's status
            is_finish = True
            for d_yaml in k8s_resource.deployments:
                metadata = d_yaml['metadata']
                d_name = metadata['name']
                if not self.__wait_for_k8s_status(adapter, d_name, K8S_DEPLOYMENT_STATUS.AVAILABLE):
                    is_finish = False
                    break

            if is_finish:
                self.log.debug("k8s deployment succeeds: %s" % str(context))
                self.__on_create_success(context)
                return True
            else:
                self.log.error("k8s deployment fails: %s" % str(context))
                self._internal_rollback(context)

        except Exception as e:
            self.__on_message("k8s_service_create_failed", context)

        return False

    def schedule_start_k8s_service(self, context):
        experiment = Experiment.objects.get(id=context.experiment_id)
        virtual_env = experiment.virtual_environments[0]
        adapter = self.__get_adapter_from_ctx(K8SServiceAdapter, context)

        try:
            if adapter.get_deployment_status(virtual_env.name) != K8S_DEPLOYMENT_STATUS.PAUSE:
                raise RuntimeError("K8s Service not has paused")

            k8s_resource = virtual_env.k8s_resource
            for deploy in k8s_resource.deployments:
                metadata = deploy['metadata']
                d_name = metadata['name']
                adapter.start_k8s_deployment(d_name)
                if not self.__wait_for_k8s_status(adapter, virtual_env.name, K8S_DEPLOYMENT_STATUS.AVAILABLE):
                    raise RuntimeError("Deploy {} start error".format(d_name))
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
        # TODO: try to abstract common behavior

    @staticmethod
    def __create_useful_k8s_resource(hackathon, env_name, template_content):
        """ helper func to generate available and unique resources yaml

        Currently supported resources
            - Deployment
            - Service
            - StatefulSet
            - PersistentVolumeClaim

        :param hackathon:
        :param env_name:
        :param template_content:
        :return:
        """
        _experiments = Experiment.objects(hackathon=hackathon).all()
        _virtual_envs = []
        for e in _experiments:
            _virtual_envs += list(e.virtual_environments)

        _names = [v.name for v in _virtual_envs]
        count = 0
        name = None
        while count < 100:
            count += 1
            name = "{}-{}".format(env_name, count)
            if name not in _names:
                break
        if count >= 100:
            raise RuntimeError("Can't get useful env name.")

        k8s_env = K8sEnvironment(
            name=name,
            deployments=template_content.get_resource("deployment"),
            services=template_content.get_resource("service"),
            statefulsets=template_content.get_resource("statefulset"),
            persistent_volume_claims=template_content.get_resource("persistentvolumeclaim"),
        )

        return k8s_env

    def __wait_for_k8s_status(self, adapter, service_name, status):
        # Wait up to 15 minutes
        attempts = 60

        while attempts:
            self.log.debug("__wait_for_k8s_status, service_name: %s, target status: %d, remaining attempts: %d"
                           % (service_name, status, attempts))
            attempts -= 1
            time.sleep(15)
            if adapter.get_deployment_status(service_name) == status:
                return True
        return False

    @staticmethod
    def __get_adapter_from_ctx(adapter_class, context):
        template_content = context.template_content
        cluster = template_content.cluster_info
        return adapter_class(cluster.api_url, cluster.token, cluster.namespace)

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


class TemplateRender:

    def __init__(self, resource_name, resource_type, yml, labels):
        self.resource_name = resource_name
        self.resource_type = resource_type
        self.yaml = yml
        self.labels = labels

    def __render_deploy(self):
        metadata = self.yaml['metadata']
        metadata["name"] = "{}-{}".format(self.resource_name, metadata["name"])
        deploy_labels = metadata.get("labels") or {}
        deploy_labels.update(self.labels)
        metadata['labels'] = deploy_labels

        spec = self.yaml['spec']
        pod_template = spec['template']
        pod_metadata = pod_template['metadata']
        pod_labels = pod_metadata.get("labels") or {}
        pod_labels.update(self.labels)
        pod_metadata['labels'] = pod_labels

        if "selector" in spec:
            match_labels = spec['selector'].get("matchLabels") or {}
            match_labels.update(self.labels)
            spec['selector']['matchLabels'] = match_labels

        # Make sure PVC is no conflict
        if "volumes" in spec:
            for v in spec['volumes']:
                if "persistentVolumeClaim" not in v:
                    continue
                pvc = v['persistentVolumeClaim']
                pvc['claimName'] = "{}-{}".format(self.resource_name, pvc['claimName'])

    def __render_svc(self):
        metadata = self.yaml['metadata']
        metadata["name"] = "{}-{}".format(self.resource_name, metadata["name"])
        svc_labels = metadata.get("labels") or {}
        svc_labels.update(self.labels)
        metadata['labels'] = svc_labels

        spec = self.yaml['spec']
        label_selector = spec.get("selector") or {}
        label_selector.update(self.labels)

    def __render_stateful_set(self):
        metadata = self.yaml['metadata']
        metadata["name"] = "{}-{}".format(self.resource_name, metadata["name"])
        ss_labels = metadata.get("labels") or {}
        ss_labels.update(self.labels)
        metadata['labels'] = ss_labels

        spec = self.yaml['spec']
        if "selector" in spec:
            match_labels = spec['selector'].get("matchLabels") or {}
            match_labels.update(self.labels)
            spec['selector']['matchLabels'] = match_labels

    def __render_pvc(self):
        metadata = self.yaml['metadata']
        metadata["name"] = "{}-{}".format(self.resource_name, metadata["name"])
        pvc_labels = metadata.get("labels") or {}
        pvc_labels.update(self.labels)
        metadata['labels'] = pvc_labels
