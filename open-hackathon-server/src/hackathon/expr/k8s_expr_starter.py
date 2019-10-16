# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
import yaml
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
        _env_name = "{}-{}".format(_env_name, "".join(random.sample(string.lowercase, 6)))

        try:
            if not _virtual_envs:
                # Get None VirtualEnvironment, create new one:
                labels = {
                    "hacking.kaiyuanshe.cn/hackathon": str(hackathon.id),
                    "hacking.kaiyuanshe.cn/experiment": str(experiment.id),
                    "hacking.kaiyuanshe.cn/virtual_environment": _env_name,
                }
                k8s_env = self.__create_useful_k8s_resource(_env_name, template_content, labels)

                experiment.virtual_environments.append(VirtualEnvironment(
                    provider=VE_PROVIDER.K8S,
                    name=_env_name,
                    k8s_resource=k8s_env,
                    status=VEStatus.INIT,
                    remote_provider=VERemoteProvider.Guacamole))

                experiment.status = EStatus.INIT
                experiment.save()
                self.log.debug("virtual_environments %s created, creating k8s..." % _env_name)
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
            self.__schedule_stop(context)
        except Exception as e:
            self.log.error(e)
            experiment.status = EStatus.FAILED
            experiment.save()
            return internal_server_error('Failed stopping k8s')

    def _internal_rollback(self, context):
        self.__schedule_stop(context)

    def __schedule_start(self, ctx):
        self.scheduler.add_once("k8s_service", "schedule_start_k8s_service", context=ctx,
                                id="schedule_setup_" + str(ctx.experiment_id), seconds=0)

    def __schedule_stop(self, ctx):
        self.scheduler.add_once("k8s_service", "schedule_stop_k8s_service", context=ctx,
                                id="schedule_stop_" + str(ctx.experiment_id), seconds=0)

    def schedule_start_k8s_service(self, context):
        experiment = Experiment.objects.get(id=context.experiment_id)
        virtual_env = experiment.virtual_environments[0]
        k8s_resource = virtual_env.k8s_resource
        adapter = self.__get_adapter_from_ctx(K8SServiceAdapter, context)

        try:
            for pvc in k8s_resource.persistent_volume_claims:
                adapter.create_k8s_pvc(pvc)

            for s in k8s_resource.services:
                adapter.create_k8s_service(s)

            for d in k8s_resource.deployments:
                adapter.create_k8s_deployment(d)

            for s in k8s_resource.stateful_sets:
                adapter.create_k8s_statefulset(s)

            self.__wait_for_k8s_ready(adapter, k8s_resource.deployments, k8s_resource.stateful_sets)
            self.__config_endpoint(experiment, k8s_resource.services)
        except Exception as e:
            self.log.error("k8s_service_start_failed: {}".format(e))

    def schedule_stop_k8s_service(self, context):
        experiment = Experiment.objects.get(id=context.experiment_id)
        virtual_envs = experiment.virtual_environments
        adapter = self.__get_adapter_from_ctx(K8SServiceAdapter, context)
        try:
            for virtual_env in virtual_envs:
                for d in virtual_env.deployments:
                    adapter.delete_k8s_deployment(d['metadata']['name'])

                for pvc in virtual_env.persistent_volume_claims:
                    adapter.delete_k8s_pvc(pvc['metadata']['name'])

                for s in virtual_env.stateful_sets:
                    adapter.delete_k8s_statefulset(s['metadata']['name'])

                for s in virtual_env.services:
                    adapter.delete_k8s_service(s['metadata']['name'])

            self.log.debug("k8s_service_stop: {}".format(context))
        except Exception as e:
            self.log.error("k8s_service_stop_failed: {}".format(e))
        experiment.delete()

    @staticmethod
    def __create_useful_k8s_resource(env_name, template_content, labels):
        """ helper func to generate available and unique resources yaml

        Currently supported resources
            - Deployment
            - Service
            - StatefulSet
            - PersistentVolumeClaim

        :param env_name:
        :param template_content:
        :param labels:
        :return:
        """

        k8s_env = K8sEnvironment(
            name=env_name,
            deployments=[
                yaml.dump(TemplateRender(env_name, "deployment", d, labels).render())
                for d in template_content.get_resource("deployment")
            ],
            services=[
                yaml.dump(TemplateRender(env_name, "service", s, labels).render())
                for s in template_content.get_resource("service")
            ],
            statefulsets=[
                yaml.dump(TemplateRender(env_name, "statefulset", s, labels).render())
                for s in template_content.get_resource("statefulset")
            ],
            persistent_volume_claims=[
                yaml.dump(TemplateRender(env_name, "statefulset", p, labels).render())
                for p in template_content.get_resource("persistentvolumeclaim")
            ],
        )

        return k8s_env

    @staticmethod
    def __wait_for_k8s_ready(adapter, deployments, stateful_sets):
        # TODO Sleep for ready is NOT GOOD IDEA, Why not use watch api?
        # Wait up to 30 minutes
        end_time = int(time.time()) + 60 * 60 * 30

        for d_yaml in deployments:
            d = yaml.load(d_yaml)
            while adapter.get_deployment_status(d['metadata']['name']) != K8S_DEPLOYMENT_STATUS.AVAILABLE:
                time.sleep(1)
                if int(time.time()) > end_time:
                    raise RuntimeError("Start deployment error: Timeout")

        for s in stateful_sets:
            # TODO check statfulSet status
            pass

    def __config_endpoint(self, expr, services):
        self.log.debug("experiment started %s successfully. Setting remote parameters." % expr.id)
        # set experiment status
        # update the status of virtual environment
        virtual_env = expr.virtual_environments[0]
        template = expr.template
        cluster = template.k8s_cluster
        ingress = cluster.ingress
        if not ingress or not services:
            self.log.info("Has no endpoint config")
            return
        assert isinstance(ingress, list)
        svc = None
        for s in services:
            if s.get("type") == "NodePort":
                svc = s
                break
        if not svc:
            return

        ports = svc.get("ports", [])
        if not ports:
            self.log.info("Has no endpoint config")
            return
        public_port = ports[0].get("nodePort")
        if not public_port:
            return

        gc = {
            K8S_UNIT.REMOTE_PARAMETER_NAME: virtual_env.name,
            K8S_UNIT.REMOTE_PARAMETER_DISPLAY_NAME: svc['metadata']['name'],
            K8S_UNIT.REMOTE_PARAMETER_HOST_NAME: random.choice(ingress),
            K8S_UNIT.REMOTE_PARAMETER_PROTOCOL: "vnc",
            K8S_UNIT.REMOTE_PARAMETER_PORT: public_port,
            # K8S_UNIT.REMOTE_PARAMETER_USER_NAME: "",
            # K8S_UNIT.REMOTE_PARAMETER_PASSWORD: "",
        }
        self.log.debug("expriment %s remote parameters: %s" % (expr.id, str(gc)))
        virtual_env.remote_paras = gc

        virtual_env.status = VEStatus.RUNNING
        expr.status = EStatus.RUNNING
        expr.save()

    @staticmethod
    def __get_adapter_from_ctx(adapter_class, context):
        template_content = context.template_content
        cluster = template_content.cluster_info
        return adapter_class(cluster.api_url, cluster.token, cluster.namespace)


class TemplateRender:
    """
    Types:
        - Deployment
        - Service
        - StatefulSet
        - PersistentVolumeClaim
    """

    def __init__(self, resource_name, resource_type, yml, labels):
        self.resource_name = resource_name
        self.resource_type = str(resource_type).lower()
        self.yaml = yml
        self.labels = labels

    def render(self):

        if self.resource_type == "deployment":
            return self.__render_deploy()

        if self.resource_type == "service":
            return self.__render_svc()

        if self.resource_type == "statefulset":
            return self.__render_stateful_set()

        if self.resource_type == "persistentvolumeclaim":
            return self.__render_pvc()

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
        return self.yaml

    def __render_svc(self):
        metadata = self.yaml['metadata']
        metadata["name"] = "{}-{}".format(self.resource_name, metadata["name"])
        svc_labels = metadata.get("labels") or {}
        svc_labels.update(self.labels)
        metadata['labels'] = svc_labels

        spec = self.yaml['spec']
        label_selector = spec.get("selector") or {}
        label_selector.update(self.labels)
        return self.yaml

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
        return self.yaml

    def __render_pvc(self):
        metadata = self.yaml['metadata']
        metadata["name"] = "{}-{}".format(self.resource_name, metadata["name"])
        pvc_labels = metadata.get("labels") or {}
        pvc_labels.update(self.labels)
        metadata['labels'] = pvc_labels
        return self.yaml
