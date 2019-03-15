
# -*- coding: utf-8 -*-
"""
Copyright (c) KaiYuanShe.  All rights reserved.

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


import unittest
from mock import Mock

# setup import path
try:
    import hackathon  # noqa
except ImportError:
    import os
    import sys
    BASE_DIR = os.path.dirname(__file__)
    sys.path.append(os.path.realpath(os.path.join(BASE_DIR, "..", "..", "..", "src")))

from hackathon.hk8s.k8s_service_adapter import K8SServiceAdapter
from hackathon import Context
import test_k8s_conf

class K8SServiceAdapterTest(unittest.TestCase):
    def setUp(self):
        self.service = K8SServiceAdapter(test_k8s_conf.kube_config)

    #prerequisites:
    #1, change mode of files in /var/log/open-hackathon to 777
    #2, copy kube config file to ~/.kube/config (kubeconfig.json)
    #3, copy yaml file to ~/.kube/yaml (nginx-deployment.yaml)

    #@unittest.skip("test require real connection to k8s server")
    def test_k8s_create_deployment(self):
        self.assertTrue(self.service.create_k8s_deployment_with_yaml( test_k8s_conf.yaml_file,
                        test_k8s_conf.deplyment_name, test_k8s_conf.namespace))

