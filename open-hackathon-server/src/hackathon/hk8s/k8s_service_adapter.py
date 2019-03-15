# -*- coding: utf-8 -*-
"""
Copyright (c) KaiYuanShe  All rights reserved.

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import sys


from os import path
from kubernetes import client, config, utils

from hackathon import RequiredFeature, Component, Context
from hackathon.constants import HEALTH, HEALTH_STATUS, HACKATHON_CONFIG, CLOUD_PROVIDER
from hackathon.hazure.service_adapter import ServiceAdapter

sys.path.append("..")

__all__ = ["K8SServiceAdapter"]

class K8SServiceAdapter(ServiceAdapter):

    def __init__(self, config_file):

        self.default_kube_config_file = "./kubeconfig.json"
#        self.k8s_client = client.ApiClient()


        if config_file == None :
            self.kube_config_file = self.default_config_file
        else:
            self.kube_config_file = config_file

#        try:
#            config.load_kube_config(self.kube_config_file)
            #self.k8s_api = client.AppsV1Api(client.ApiClient(config))
#        except Exception as e:
#            self.log.error(e)

    def create_k8s_deployment_with_yaml(self, yaml, name, namespace):
        try:
            #k8s_api is reinitialized with create_from_yaml
            config.load_kube_config(self.kube_config_file)
            self.k8s_client = client.ApiClient()
            self.k8s_api = utils.create_from_yaml(self.k8s_client, yaml)
            #see https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#read_namespaced_deployment
            resp = self.k8s_api.read_namespaced_deployment(name, namespace)
            return format(resp.metadata.name)
        except Exception as e:
            if 'Confilct' == e.reason:
                return name
            else:
                self.log.error(e)
                return None

    def deployment_exists(self, name):
        return name in self.list_deployments(name)

#        v1 = client.ExtensionsV1beta1Api()
#        ret = v1.list_deployment_for_all_namespaces(watch=False)
#        for i in ret.items:
#            if name == i.metadata.name:
#                return true
#        return false

    def report_health(self):
        raise NotImplementedError()



    def start_k8s_service(self, name, namespace):
        raise NotImplementedError()


    def stop_k8s_service(self):
        raise NotImplementedError()


    def ping(self, url, timeout=20):
        pass

#    def get_deployment_detail_by_name(self, deployment_name):
#        return

    def list_deployments(self, deployment_name, timeout=20):
        list = []
        v1 = client.ExtensionsV1beta1Api()
        #see https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#list_deployment_for_all_namespaces
        ret = v1.list_deployment_for_all_namespaces(watch=False)

        for i in ret.items:
            list.append(i.metadata.name)

        return list

    def get_deployment_by_name(self, deployment_name, namespace):
        #https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#read_namespaced_deployment
        deps = self.k8s_api.read_namespaced_deployment(deployment_name, namespace)
        return deps.metadata.available

#if __name__ == '__main__':
#    main()
