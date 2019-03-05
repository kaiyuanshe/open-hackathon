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
from hackathon.hazure import ServiceAdapter

sys.path.append("..")

__all__ = ["K8SServiceAdapter"]

class K8SServiceAdapter(ServiceAdapter):
    k8s_client = client.ApiClient()
    default_config_file = "./kubeconfig.json"

    def __init__(self, config_file):
        try:
            if config_file == None : config_file = default_config_file
            config.load_kube_config(config_file)
            #self.k8s_client = client.ApiClient()
        except Exception as e:
            self.log.error(e)
            return False
        return True

    def create_k8s_deployment_with_yaml(self, yaml, name, namespace):
        try:
            #TODO: k8s_api should be a global variable in this file, need further investigation how
            k8s_api = utils.create_from_yaml(self.k8s_client, yaml)
            #see https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#read_namespaced_deployment
            resp = k8s_api.read_namespaced_deployment(name, namespace)
            return format(deps.metadata.name)
        except Exception as e:
            if 'Exists' in e:
                return name
            else:
                self.log.error(e)
                return None

    def deployment_exists(self, name):
        return name in list_deployments(name)

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
         try:
            req = requests.get(url, timeout=timeout)
            return req.status_code == 200 and req.content == 'OK'
         except Exception as e:
            return False


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
