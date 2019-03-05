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
import sys

sys.path.append("..")

from template_constants import K8S_UNIT
from template_unit import TemplateUnit
from hackathon.constants import VE_PROVIDER




__all__ = ["K8STemplateUnit"]


class K8STemplateUnit(TemplateUnit):
    """
    Smallest unit in k8s template
    """

    def __init__(self, dic):
        super(DockerTemplateUnit, self).__init__(VE_PROVIDER.DOCKER)
        self.dic = self.load_default_config()
        for key, value in dic.iteritems():
            self.dic[key] = value

    def load_default_config(self):
        dic = {
            K8S_UNIT.NAME: 'Kubernetes',
            K8S_UNIT.YAML_FILE: 'default location',
            K8S_UNIT.DEPLOYMENT_NAME: 'default name',
            K8S_UNIT.CONFIG: ""
        }
        return dic

    def set_name(self, name):
        self.dic[K8S_UNIT.NAME] = name

    def get_name(self):
        return self.dic[K8S_UNIT.NAME]


    def set_yaml_file(self, yaml):
        self.dic[K8S_UNIT.YAML_FILE] = yaml

    def get_yaml_file(self):
        return self.dic[K8S_UNIT.YAML_FILE]

    def set_deployment_name(self, deployment):
        self.dic[K8S_UNIT.DEPLOYMENT_NAME] = deployment

    def get_deployment_name(self):
        return self.dic[K8S_UNIT.DEPLOYMENT_NAME]

    def set_config(self, config):
        self.dic[K8S_UNIT.DEPLOYMENT_NAME] = config

    def get_config(self):
        return self.dic[K8S_UNIT.CONFIG]
