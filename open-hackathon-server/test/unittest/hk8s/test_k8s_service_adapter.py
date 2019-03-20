# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
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

    #@unittest.skip("skip test_k8s_create_deployment")
    def test_k8s_create_deployment(self):
        self.assertTrue(self.service.create_k8s_deployment_with_yaml( test_k8s_conf.yaml_file,
                        test_k8s_conf.deplyment_name, test_k8s_conf.namespace))

    #@unittest.skip("skip test_k8s_deployment_exists")
    def test_k8s_deployment_exists(self):
        self.assertTrue(self.service.deployment_exists(test_k8s_conf.deplyment_name))
