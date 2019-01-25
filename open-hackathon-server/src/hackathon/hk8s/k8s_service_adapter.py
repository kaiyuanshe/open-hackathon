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

    def create_depolyment_from_yaml(self):
        k8s_api = utils.create_from_yaml(self.k8s_client, "nginx-deployment.yaml")
        deps = k8s_api.read_namespaced_deployment("nginx-test", "default")
#        self.log.debug("Deployment {0} created".format(deps.metadata.name))
        return deps.metadata.name

    def report_health(self):
        return



    def start_container(self):
        return


    def stop_container(self):
        return



    def ping(self, docker_host, timeout=20):
        return

#    def get_deployment_detail_by_name(self, deployment_name):
#        return

    def list_deployments(self, deployment_name, timeout=20):
        return

    def get_deployment_by_name(self, deployment_name):
        deps = self.k8s_api.read_namespaced_deployment(deployment_name, "default")
        return deps.metadata.name

#if __name__ == '__main__':
#    main()
