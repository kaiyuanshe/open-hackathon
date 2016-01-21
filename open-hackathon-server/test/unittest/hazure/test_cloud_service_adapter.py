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

__author__ = "rapidhere"

import unittest
from mock import Mock

from azure.common import AzureMissingResourceHttpError, AzureHttpError

# setup import path
try:
    import hackathon  # noqa
except ImportError:
    import os
    import sys
    BASE_DIR = os.path.dirname(__file__)
    sys.path.append(os.path.realpath(os.path.join(BASE_DIR, "..", "..", "..", "src")))

from hackathon.hazure.cloud_service_adapter import CloudServiceAdapter
from hackathon.hazure.constants import ASYNC_OP_RESULT
from hackathon import Context
import test_conf


class CloudServiceAdapterTest(unittest.TestCase):
    def setUp(self):
        self.service = CloudServiceAdapter(
            test_conf.subscription_id,
            test_conf.pem_url,
            host=test_conf.management_host)

    def tearDown(self):
        pass

    @unittest.skip("heavy test require real connection to azure cloud")
    def test_cloud_service_exisits_real(self):
        self.assertTrue(self.service.cloud_service_exists(
            test_conf.azure_cloud_service_name_should_exist))

        self.assertFalse(self.service.cloud_service_exists(
            test_conf.meanless_name))

    def test_cloud_service(self):
        mock = Mock()
        self.service.service.get_hosted_service_properties = mock

        mock.return_value = True
        self.assertTrue(self.service.cloud_service_exists(
            test_conf.meanless_name))

        mock.return_value = None
        self.assertFalse(self.service.cloud_service_exists(
            test_conf.meanless_name))

        mock.side_effect = AzureMissingResourceHttpError(233, 233)
        self.assertFalse(self.service.cloud_service_exists(
            test_conf.meanless_name))

    @unittest.skip("heavy test require real connection to azure cloud")
    def test_create_cloud_service_real(self):
        print "After run this test, don't forget to delete resources on azure cloud"

        self.assertTrue(self.service.create_cloud_service(
            test_conf.azure_cloud_service_to_create["name"],
            test_conf.azure_cloud_service_to_create["label"],
            test_conf.azure_cloud_service_to_create["location"]))

        self.assertTrue(self.service.cloud_service_exists(
            test_conf.azure_cloud_service_to_create["name"]))

        self.assertFalse(self.service.create_cloud_service(
            test_conf.azure_cloud_service_to_create["name"],
            test_conf.azure_cloud_service_to_create["label"],
            test_conf.azure_cloud_service_to_create["location"]))

    def test_creat_hosted_service(self):
        mock_create = Mock()
        mock_wait = Mock()
        self.service.service.create_cloud_service = mock_create
        self.service.service.wait_for_operation_status = mock_wait

        mock_create.return_value = Context(request_id=test_conf.meanless_id)
        mock_wait.return_value = Context(status=ASYNC_OP_RESULT.SUCCEEDED)
        self.assertTrue(self.service.create_cloud_service(
            test_conf.meanless_name,
            test_conf.meanless_name,
            test_conf.meanless_name))

        mock_create.side_effect = AzureHttpError(233, 233)
        self.assertFalse(self.service.create_cloud_service(
            test_conf.meanless_name,
            test_conf.meanless_name,
            test_conf.meanless_name))

    def test_create_cloud_service(self):
        mock_exist = Mock()
        mock_create = Mock()
        mock_db = Mock()
        self.service.cloud_service_exists = mock_exist
        self.service.create_cloud_service = mock_create
        self.service.db = mock_db

        mock_exist.return_value = False
        mock_create.return_value = False
        self.assertFalse(self.service.create_cloud_service(
            test_conf.meanless_id,
            test_conf.meanless_name,
            test_conf.meanless_name,
            test_conf.meanless_name))

        # TODO: ignored db check
        mock_exist.return_value = True
        mock_create.return_value = True
        self.assertTrue(self.service.create_cloud_service(
            test_conf.meanless_id,
            test_conf.meanless_name,
            test_conf.meanless_name,
            test_conf.meanless_name))
