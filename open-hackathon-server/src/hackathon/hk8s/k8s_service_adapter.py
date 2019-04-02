# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

from os import path
import yaml as yaml_tool
from kubernetes import client, utils
from kubernetes.client.rest import ApiException

from hackathon import RequiredFeature, Component, Context
from hackathon.constants import HEALTH, HEALTH_STATUS, HACKATHON_CONFIG, K8S_DEPLOYMENT_STATUS
from hackathon.hazure.service_adapter import ServiceAdapter

from .yaml_helper import YamlBuilder
from .errors import DeploymentError, ServiceError

__all__ = ["K8SServiceAdapter"]


class K8SServiceAdapter(ServiceAdapter):

    def __init__(self, api_url, token):
        configuration = client.Configuration()
        configuration.host = api_url
        configuration.api_key['authorization'] = 'bearer ' + token
        # FIXME import ca cert file?
        configuration.verify_ssl = False

        self.api_client = client.ApiClient(configuration)
        super(K8SServiceAdapter, self).__init__(self.api_client)

    def create_k8s_environment(self, namespace, images, ports, **kwargs):
        # auto create deployment and service for environment
        yb = YamlBuilder(namespace, images, ports, **kwargs)
        yb.build()

        for s in yb.svc_yamls:
            self.create_k8s_service(namespace, s)
        for d in yb.deploy_yamls:
            self.start_k8s_deployment(namespace, d)

    def deployment_exists(self, name):
        return name in self.list_deployments(name)

    def report_health(self):
        try:
            api_instance = client.VersionApi(self.api_client)
            result = api_instance.get_code()
            assert result, "Get nothing about cluster version from apiServer."
            return {HEALTH.STATUS: HEALTH_STATUS.OK}
        except ApiException as e:
            self.log.error(e)
            return {
                HEALTH.STATUS: HEALTH_STATUS.ERROR,
                HEALTH.DESCRIPTION: "Get cluster info error: {}".format(e),
            }

    def start_k8s_deployment(self, namespace, yaml):
        api_instance = client.AppsV1Api(self.api_client)
        if isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.load(yaml)
        assert isinstance(yaml, dict), "Start a deployment without legal yaml."
        metadata = yaml.get("metadata", {})
        deploy_name = metadata.get("name")

        try:
            _deploy = self.get_deployment_by_name(namespace, deploy_name)
            if _deploy:
                self.log.info("Starting existed deployment: {}".format(deploy_name))
                _spec = _deploy.spec
                if _spec.replicas > 0:
                    return deploy_name
                _spec.replicas = 1
                api_instance.patch_namespaced_deployment(deploy_name, namespace, _deploy)
                return deploy_name
            _deploy = api_instance.create_namespaced_deployment(namespace, yaml)
        except ApiException as e:
            self.log.error("Start deployment error: {}".format(e))
            raise DeploymentError("Start deployment error: {}".format(e))
        return deploy_name

    def get_deployment_by_name(self, namespace, deployment_name):
        api_instance = client.AppsV1Api(self.api_client)
        try:
            _deploy = api_instance.read_namespaced_deployment_status(deployment_name, namespace)
        except ApiException as e:
            self.log.error(e)
            return None
        return _deploy

    def get_deployment_status(self, namespace, deployment_name):
        _deploy = self.get_deployment_by_name(namespace, deployment_name)
        _status = _deploy.status
        if _status.replicas == 0:
            return K8S_DEPLOYMENT_STATUS.PAUSE
        if _status.replicas == _status.ready_replicas:
            return K8S_DEPLOYMENT_STATUS.READY
        if _status.unavailable_replicas > 0:
            return K8S_DEPLOYMENT_STATUS.ERROR
        return K8S_DEPLOYMENT_STATUS.PENDING

    def pause_k8s_deployment(self, deployment_name, namespace):
        _deploy = self.get_deployment_by_name(namespace, deployment_name)
        _spec = _deploy.spec
        _spec.replicas = 0
        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.patch_namespaced_deployment(deployment_name, namespace, _deploy)
        except ApiException as e:
            self.log.error("Pause deployment error: {}".format(e))
            raise DeploymentError("Pause {} error {}".format(deployment_name, e))

    def delete_k8s_deployment(self, namespace, deployment_name):
        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_deployment(deployment_name, namespace)
        except ApiException as e:
            self.log.error("Delete deployment error: {}".format(e))
            raise DeploymentError("Delete {} error {}".format(deployment_name, e))

    def create_k8s_service(self, namespace, yaml):
        if isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.load(yaml)
        assert isinstance(yaml, dict), "Create a service without legal yaml."

        api_instance = client.CoreV1Api(self.api_client)
        try:
            api_instance.create_namespaced_service(namespace, yaml)
        except ApiException as e:
            self.log.error("Create service error: {}".format(e))
            raise ServiceError("Create service error: {}".format(e))

    def delete_k8s_service(self, namespace, service_name):
        api_instance = client.CoreV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_service(service_name, namespace)
        except ApiException as e:
            self.log.error("Delete service error: {}".format(e))
            raise ServiceError("Delete service error: {}".format(e))

    def ping(self, url, timeout=20):
        report = self.report_health()
        return report[HEALTH.STATUS] == HEALTH_STATUS.OK

    def list_deployments(self, namespace=None, labels=None, timeout=20):
        _deployments = []
        kwargs = {"timeout_seconds": timeout, "watch": False}
        if labels and isinstance(labels, dict):
            label_selector = ",".join(["{}={}".format(k, v) for k, v in labels.items()])
            kwargs['label_selector'] = label_selector

        apps_v1_group = client.AppsV1Api(self.api_client)
        try:
            if not namespace:
                ret = apps_v1_group.list_deployment_for_all_namespaces(**kwargs)
            else:
                ret = apps_v1_group.list_namespaced_deployment(namespace, **kwargs)
        except ApiException as e:
            self.log.error(e)
            return []

        for i in ret.items:
            _deployments.append(i.metadata.name)
        return _deployments
