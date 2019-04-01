# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

from os import path
from kubernetes import client, utils
from kubernetes.client.rest import ApiException

from hackathon import RequiredFeature, Component, Context
from hackathon.constants import HEALTH, HEALTH_STATUS, HACKATHON_CONFIG, CLOUD_PROVIDER
from hackathon.hazure.service_adapter import ServiceAdapter

sys.path.append("..")

__all__ = ["K8SServiceAdapter"]


class K8SServiceAdapter(ServiceAdapter):

    def __init__(self):
        # TODO add kube config
        configuration = client.Configuration()
        configuration.host = 'KUBE_API_SERVER'
        configuration.api_key['authorization'] = 'bearer ' + 'SERVICE_ACCOUNT_TOKEN'
        # FIXME import ca cert file?
        configuration.verify_ssl = False

        self.api_client = client.ApiClient(configuration)
        super(K8SServiceAdapter, self).__init__(self.api_client)

    def create_k8s_deployment_with_yaml(self, yaml, name, namespace):
        try:
            api_instance = utils.create_from_yaml(self.api_client, yaml)
            # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md
            resp = api_instance.read_namespaced_deployment(name, namespace)
            return format(resp.metadata.name)
        except ApiException as e:
            self.log.error(e)
            return None

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

    def start_k8s_service(self, name, namespace):
        raise NotImplementedError()

    def pause_k8s_service(self):
        raise NotImplementedError()

    def stop_k8s_service(self):
        raise NotImplementedError()

    def ping(self, url, timeout=20):
        report = self.report_health()
        return report[HEALTH.STATUS] == HEALTH_STATUS.OK

    def list_deployments(self, namespace=None, timeout=20):
        _deployments = []
        apps_v1_group = client.AppsV1Api(self.api_client)
        if not namespace:
            ret = apps_v1_group.list_deployment_for_all_namespaces(timeout_seconds=timeout, watch=False)
        else:
            ret = apps_v1_group.list_namespaced_deployment(namespace, timeout_seconds=timeout, watch=False)

        for i in ret.items:
            _deployments.append(i.metadata.name)
        return _deployments

    def get_deployment_by_name(self, deployment_name, namespace):
        raise NotImplementedError()
        # https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#read_namespaced_deployment
        # deps = self.k8s_api.read_namespaced_deployment(deployment_name, namespace)
        # return deps.metadata.available
