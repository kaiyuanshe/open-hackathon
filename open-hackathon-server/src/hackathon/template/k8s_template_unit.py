# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.

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

from hackathon.template.template_constants import K8S_UNIT
from hackathon.template.template_unit import TemplateUnit
from hackathon.constants import VE_PROVIDER

__all__ = ["K8STemplateUnit"]


class K8STemplateUnit(TemplateUnit):
    """
    Smallest unit in k8s template
    """

    def __init__(self, dic):
        super(K8STemplateUnit, self).__init__(VE_PROVIDER.K8S)
        self.dic = self.load_default_config()
        for key, value in dic.items():
            self.dic[key] = value

    @staticmethod
    def load_default_config():
        dic = {
            K8S_UNIT.NAME: 'Kubernetes',
            K8S_UNIT.CONFIG_CLUSTER: {
                K8S_UNIT.CONFIG_API_SERVER: "",
                K8S_UNIT.CONFIG_API_TOKEN: "",
                K8S_UNIT.CONFIG_NAMESPACES: "",
            },
            K8S_UNIT.IMAGES: [
                {
                    K8S_UNIT.IMAGES_IMAGE: "busybox",
                }
            ],
            K8S_UNIT.PORTS: [
                {
                    K8S_UNIT.PORTS_NAME: 'Deploy',
                    K8S_UNIT.PORTS_PORT: 22,
                    K8S_UNIT.PORTS_PUBLIC: True,
                    K8S_UNIT.PORTS_PROTOCOL: 'TCP',
                    K8S_UNIT.PORTS_PUBLIC_PORT: 22,
                }
            ],
            K8S_UNIT.REMOTE: {
                K8S_UNIT.REMOTE_PROVIDER: 'guacamole',
                K8S_UNIT.REMOTE_PROTOCOL: 'ssh',
                K8S_UNIT.REMOTE_USERNAME: 'root',
                K8S_UNIT.REMOTE_PASSWORD: 'root',
                K8S_UNIT.REMOTE_PORT: 22,
            },
            K8S_UNIT.RESOURCES: {
                K8S_UNIT.RESOURCES_REQUESTS: {
                    K8S_UNIT.RESOURCES_REQUESTS_CPU: "1",
                    K8S_UNIT.RESOURCES_REQUESTS_MEM: "3Gi",
                },
                K8S_UNIT.RESOURCES_LIMITS: {
                    K8S_UNIT.RESOURCES_LIMITS_CPU: "2",
                    K8S_UNIT.RESOURCES_LIMITS_MEM: "4Gi",
                },
            }
        }
        return dic

    def set_name(self, name):
        self.dic[K8S_UNIT.NAME] = name

    def get_name(self):
        return self.dic[K8S_UNIT.NAME]

    def get_description(self):
        return self.get_name()

    def get_type(self):
        return "kubernetes"

    def get_cluster(self):
        return self.dic[K8S_UNIT.CONFIG_CLUSTER]

    def set_cluster(self, cluster_info):
        self.dic[K8S_UNIT.CONFIG_CLUSTER] = cluster_info

    def get_ports(self):
        return self.dic[K8S_UNIT.PORTS]

    def set_ports(self, ports):
        self.dic[K8S_UNIT.PORTS] = ports

    def get_remote(self):
        return self.dic[K8S_UNIT.REMOTE]

    def set_remote(self, remote):
        self.dic[K8S_UNIT.REMOTE] = remote

    def get_images(self):
        return self.dic[K8S_UNIT.IMAGES]

    def set_images(self, images):
        assert isinstance(images, list)
        self.dic[K8S_UNIT.IMAGES] = images

    def get_resources(self):
        return self.dic[K8S_UNIT.RESOURCES]

    def set_resources(self, resources):
        self.dic[K8S_UNIT.RESOURCES] = resources

    def __getattr__(self, item):
        if item in self.__getattribute__("dic"):
            return self.__getattribute__("dic")[item]
        return self.__getattribute__(item)

