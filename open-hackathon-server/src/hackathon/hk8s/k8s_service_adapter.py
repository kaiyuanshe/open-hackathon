# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning, HTTPError

import yaml as yaml_tool
from kubernetes import client
from kubernetes.client.rest import ApiException

from hackathon.constants import HEALTH, HEALTH_STATUS, K8S_DEPLOYMENT_STATUS
from hackathon.hazure.service_adapter import ServiceAdapter

from .errors import DeploymentError, ServiceError, StatefulSetError, PVCError

__all__ = ["K8SServiceAdapter"]
disable_warnings(InsecureRequestWarning)


class K8SServiceAdapter(ServiceAdapter):
    def __init__(self, api_url, token, namespace):
        configuration = client.Configuration()
        configuration.host = api_url
        configuration.api_key['authorization'] = 'bearer ' + token
        # FIXME import ca cert file?
        configuration.verify_ssl = False

        self.namespace = namespace
        self.api_url = api_url
        self.api_client = client.ApiClient(configuration)
        super(K8SServiceAdapter, self).__init__(self.api_client)

    def ping(self, timeout=20):
        report = self.report_health(timeout)
        return report[HEALTH.STATUS] == HEALTH_STATUS.OK

    def report_health(self, timeout=20):
        try:
            api_instance = client.CoreV1Api(self.api_client)
            api_instance.list_namespaced_pod(self.namespace, timeout_seconds=timeout)
            return {HEALTH.STATUS: HEALTH_STATUS.OK}
        except ApiException as e:
            self.log.error(e)
            return {
                HEALTH.STATUS: HEALTH_STATUS.ERROR,
                HEALTH.DESCRIPTION: "Get Pod info error: {}".format(e),
            }
        except HTTPError:
            return {
                HEALTH.STATUS: HEALTH_STATUS.ERROR,
                HEALTH.DESCRIPTION: "Connect K8s ApiServer {} error: connection timeout".format(self.api_url),
            }

    ###
    # Deployment
    ###

    def list_deployments(self, labels=None, timeout=20):
        _deployments = []
        kwargs = {"timeout_seconds": timeout, "watch": False}
        if labels and isinstance(labels, dict):
            label_selector = ",".join(["{}={}".format(k, v) for k, v in labels.items()])
            kwargs['label_selector'] = label_selector

        apps_v1_group = client.AppsV1Api(self.api_client)
        try:
            ret = apps_v1_group.list_namespaced_deployment(self.namespace, **kwargs)
        except ApiException as e:
            self.log.error(e)
            return []

        for i in ret.items:
            _deployments.append(i.metadata.name)
        return _deployments

    def deployment_exists(self, name):
        return self.get_deployment_by_name(name, need_raise=False) is not None

    def create_k8s_deployment(self, yaml):
        api_instance = client.AppsV1Api(self.api_client)
        if isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.load(yaml)
        assert isinstance(yaml, dict), "Start a deployment without legal yaml."
        metadata = yaml.get("metadata", {})
        deploy_name = metadata.get("name")

        try:
            if self.get_deployment_by_name(deploy_name, need_raise=False):
                raise DeploymentError("Deployment name was existed.")

            api_instance.create_namespaced_deployment(self.namespace, yaml, async_req=False)
        except ApiException as e:
            self.log.error("Start deployment error: {}".format(e))
            raise DeploymentError("Start deployment error: {}".format(e))
        return deploy_name

    def get_deployment_by_name(self, deployment_name, need_raise=True):
        api_instance = client.AppsV1Api(self.api_client)
        try:
            _deploy = api_instance.read_namespaced_deployment(deployment_name, self.namespace)
        except ApiException:
            if need_raise:
                raise DeploymentError("Deplotment {} not found".format(deployment_name))
            return None
        return _deploy

    def get_deployment_status(self, deployment_name):
        _deploy = self.get_deployment_by_name(deployment_name)
        _status = _deploy.status
        if not _status.replicas:
            return K8S_DEPLOYMENT_STATUS.PAUSE
        if _status.replicas == _status.available_replicas:
            return K8S_DEPLOYMENT_STATUS.AVAILABLE
        if _status.unavailable_replicas > 0:
            return K8S_DEPLOYMENT_STATUS.ERROR
        return K8S_DEPLOYMENT_STATUS.PENDING

    def start_k8s_deployment(self, deployment_name):
        _deploy = self.get_deployment_by_name(deployment_name)
        api_instance = client.AppsV1Api(self.api_client)
        if not _deploy:
            raise DeploymentError("Deployment {} not found".format(deployment_name))

        _spec = _deploy.spec
        if _spec.replicas > 0:
            return deployment_name
        _spec.replicas = 1
        api_instance.patch_namespaced_deployment(deployment_name, self.namespace, _deploy)
        self.log.info("Started existed deployment: {}".format(deployment_name))

    def pause_k8s_deployment(self, deployment_name):
        _deploy = self.get_deployment_by_name(deployment_name)
        _spec = _deploy.spec
        _spec.replicas = 0
        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.patch_namespaced_deployment(deployment_name, self.namespace, _deploy)
        except ApiException as e:
            self.log.error("Pause deployment error: {}".format(e))
            raise DeploymentError("Pause {} error {}".format(deployment_name, e))
        self.log.info("Paused existed deployment: {}".format(deployment_name))

    def delete_k8s_deployment(self, deployment_name):
        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_deployment(deployment_name, self.namespace)
        except ApiException as e:
            self.log.error("Delete deployment error: {}".format(e))
            raise DeploymentError("Delete {} error {}".format(deployment_name, e))
        self.log.info("Deleted existed deployment: {}".format(deployment_name))

    ###
    # Service
    ###

    def get_service_by_name(self, service_name, need_raise=True):
        api_instance = client.CoreV1Api(self.api_client)
        try:
            _svc = api_instance.read_namespaced_service(service_name, self.namespace)
        except ApiException:
            if need_raise:
                raise ServiceError("Service {} not found".format(service_name))
            return None
        return _svc.to_dict()

    def create_k8s_service(self, yaml):
        if isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.load(yaml)
        assert isinstance(yaml, dict), "Create a service without legal yaml."

        api_instance = client.CoreV1Api(self.api_client)
        try:
            svc = api_instance.create_namespaced_service(self.namespace, yaml)
            return svc.to_dict()['metadata']['name']
        except ApiException as e:
            self.log.error("Create service error: {}".format(e))
            raise ServiceError("Create service error: {}".format(e))

    def delete_k8s_service(self, service_name):
        api_instance = client.CoreV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_service(service_name, self.namespace)
        except ApiException as e:
            self.log.error("Delete service error: {}".format(e))
            raise ServiceError("Delete service error: {}".format(e))

    ###
    # StatefulSet
    ###

    def create_k8s_statefulset(self, yaml):
        if isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.load(yaml)
        assert isinstance(yaml, dict), "Create a statefulset without legal yaml."

        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.create_namespaced_stateful_set(self.namespace, yaml)
        except ApiException as e:
            self.log.error("Create StatefulSet error: {}".format(e))
            raise StatefulSetError("Create StatefulSet error: {}".format(e))

    def delete_k8s_statefulset(self, statefulset_name):
        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_stateful_set(statefulset_name, self.namespace)
        except ApiException as e:
            self.log.error("Delete StatefulSet error: {}".format(e))
            raise StatefulSetError("Delete StatefulSet error: {}".format(e))

    ###
    # PersistentVolumeClaim
    ###

    def create_k8s_pvc(self, yaml):
        if isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.load(yaml)
        assert isinstance(yaml, dict), "Create a PVC without legal yaml."

        api_instance = client.CoreV1Api(self.api_client)
        try:
            api_instance.create_namespaced_persistent_volume_claim(self.namespace, yaml)
        except ApiException as e:
            self.log.error("Create PVC error: {}".format(e))
            raise PVCError("Create PVC error: {}".format(e))

    def delete_k8s_pvc(self, pvc_name):
        api_instance = client.CoreV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_persistent_volume_claim(pvc_name, self.namespace)
        except ApiException as e:
            self.log.error("Delete PVC error: {}".format(e))
            raise PVCError("Delete PVC error: {}".format(e))
