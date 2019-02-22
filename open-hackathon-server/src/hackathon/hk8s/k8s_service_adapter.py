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
    def __init__(self):
        config.load_kube_config("jw-test-new.json")
        #self.k8s_client = client.ApiClient()
        return

    def create_k8s_deployment_with_yaml(self, yaml, name, namespace):
        k8s_api = utils.create_from_yaml(self.k8s_client, yaml)
        resp = k8s_api.read_namespaced_deployment(name, namespace)
        return str(resp.status)

    def deployment_exists(self, name):
        return name in lis_deployments(name)

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
        ret = v1.list_deployment_for_all_namespaces(watch=False)

        for i in ret.items:
            list.append(i.metadata.name)

        return list

    def get_deployment_by_name(self, deployment_name, namespace):
        deps = self.k8s_api.read_namespaced_deployment(deployment_name, namespace)
        return deps.metadata.available

#if __name__ == '__main__':
#    main()
