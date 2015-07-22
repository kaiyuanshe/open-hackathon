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
__author__ = 'Yifu Huang'

import sys
sys.path.append("../src/hackathon")

from hackathon.azureformation.service import (
    Service,
)
from hackathon.database.models import (
    AzureKey,
)
from hackathon.constants import (
    ADStatus,
    AVMStatus,
)
from mock import (
    Mock,
)
from azure.servicemanagement import (
    Deployment,
    RoleInstance,
    InstanceEndpoint,
    PersistentVMRole,
    ConfigurationSet,
    HostedService,
    Role,
    ConfigurationSetInputEndpoint,
    Operation,
)
import unittest
import mock


class ServiceTest(unittest.TestCase):

    def setUp(self):
        db_adapter_url = 'hackathon.azureformation.service.db_adapter'
        with mock.patch(db_adapter_url) as db_adapter:
            subscription_id = 'hter45sd-gf34-gfd4-ht34-ds43gree23gr'
            pem_url = '/home/azureformation.pem'
            management_host = 'das342.fdsf34.com'
            db_adapter.get_object.return_value = AzureKey(subscription_id=subscription_id,
                                                          pem_url=pem_url,
                                                          management_host=management_host)
            azure_key_id = 0
            self.service = Service(azure_key_id)

    def tearDown(self):
        pass

    def test_storage_account_exists(self):
        name = 'djfh434'
        self.service.get_storage_account_properties = Mock()
        self.service.get_storage_account_properties.return_value = None
        self.assertFalse(self.service.storage_account_exists(name))
        self.service.get_storage_account_properties.return_value = not None
        self.assertTrue(self.service.storage_account_exists(name))
        self.service.get_storage_account_properties.side_effect = Exception
        self.assertFalse(self.service.storage_account_exists(name))

    def test_cloud_service_exists(self):
        name = 'sdhsj6598'
        self.service.get_hosted_service_properties = Mock()
        self.service.get_hosted_service_properties.return_value = None
        self.assertFalse(self.service.cloud_service_exists(name))
        self.service.get_hosted_service_properties.return_value = not None
        self.assertTrue(self.service.cloud_service_exists(name))
        self.service.get_hosted_service_properties.side_effect = Exception
        self.assertFalse(self.service.cloud_service_exists(name))

    def test_deployment_exists(self):
        name = 'fhjd545'
        slot = 'df8dfkj'
        self.service.get_deployment_by_slot = Mock()
        self.service.get_deployment_by_slot.return_value = None
        self.assertFalse(self.service.deployment_exists(name, slot))
        self.service.get_deployment_by_slot.return_value = not None
        self.assertTrue(self.service.deployment_exists(name, slot))
        self.service.get_deployment_by_slot.side_effect = Exception
        self.assertFalse(self.service.deployment_exists(name, slot))

    def test_wait_for_deployment(self):
        cs_name = 'dhsj23'
        dm_name = 'fdu43f'
        sec = 1
        loop = 3
        self.service.get_deployment_by_name = Mock()
        d = Deployment()
        self.service.get_deployment_by_name.return_value = d
        self.assertFalse(self.service.wait_for_deployment(cs_name, dm_name, sec, loop))
        d.status = ADStatus.RUNNING
        self.assertTrue(self.service.wait_for_deployment(cs_name, dm_name, sec, loop))

    def test_get_virtual_machine_instance_status(self):
        d = Deployment()
        vm_name = 'dghu34'
        self.assertIsNone(self.service.get_virtual_machine_instance_status(d, vm_name))
        r = RoleInstance()
        r.instance_name = vm_name
        r.instance_status = AVMStatus.READY_ROLE
        d.role_instance_list = [r]
        self.assertEqual(self.service.get_virtual_machine_instance_status(d, vm_name), AVMStatus.READY_ROLE)

    def test_wait_for_virtual_machine(self):
        cs_name = 'dsandj2'
        dm_name = 'dshudu2'
        vm_name = 'dhfdr3f'
        sec = 1
        loop = 3
        self.service.get_deployment_by_name = Mock()
        self.service.get_deployment_by_name.return_value = None
        self.service.get_virtual_machine_instance_status = Mock()
        self.service.get_virtual_machine_instance_status.return_value = AVMStatus.STOPPED
        self.assertFalse(
            self.service.wait_for_virtual_machine(cs_name, dm_name, vm_name, sec, loop, AVMStatus.READY_ROLE)
        )
        self.service.get_virtual_machine_instance_status.return_value = AVMStatus.READY_ROLE
        self.assertTrue(
            self.service.wait_for_virtual_machine(cs_name, dm_name, vm_name, sec, loop, AVMStatus.READY_ROLE)
        )

    def test_get_virtual_machine_public_endpoint(self):
        cs_name = 'ds4'
        dm_name = 'dh3'
        vm_name = 'fd4'
        ep_name = 'fj4'
        self.service.get_deployment_by_name = Mock()
        d = Deployment()
        self.service.get_deployment_by_name.return_value = d
        self.assertIsNone(self.service.get_virtual_machine_public_endpoint(cs_name, dm_name, vm_name, ep_name))
        r = RoleInstance()
        r.role_name = vm_name
        ep = InstanceEndpoint()
        ep.name = ep_name
        ep.public_port = '10086'
        r.instance_endpoints = [ep]
        d.role_instance_list = [r]
        self.assertEqual(
            self.service.get_virtual_machine_public_endpoint(cs_name, dm_name, vm_name, ep_name),
            ep.public_port
        )

    def test_get_virtual_machine_public_ip(self):
        cs_name = 'ds65'
        dm_name = 'fdhj'
        vm_name = 'sd43'
        self.service.get_deployment_by_name = Mock()
        d = Deployment()
        self.service.get_deployment_by_name.return_value = d
        self.assertIsNone(self.service.get_virtual_machine_public_ip(cs_name, dm_name, vm_name))
        r = RoleInstance()
        r.role_name = vm_name
        ep = InstanceEndpoint()
        ep.vip = '125.125.125.125'
        r.instance_endpoints.instance_endpoints = [ep]
        d.role_instance_list = [r]
        self.assertEqual(self.service.get_virtual_machine_public_ip(cs_name, dm_name, vm_name), ep.vip)

    def test_get_virtual_machine_private_ip(self):
        cs_name = 'dsfd'
        dm_name = 'fdh4'
        vm_name = 'fgr5'
        self.service.get_deployment_by_name = Mock()
        d = Deployment()
        self.service.get_deployment_by_name.return_value = d
        self.assertIsNone(self.service.get_virtual_machine_private_ip(cs_name, dm_name, vm_name))
        r = RoleInstance()
        r.role_name = vm_name
        r.ip_address = '125.125.125.125'
        d.role_instance_list = [r]
        self.assertEqual(self.service.get_virtual_machine_private_ip(cs_name, dm_name, vm_name), r.ip_address)

    def test_virtual_machine_exists(self):
        cs_name = 'fhdjf'
        dm_name = 'fdij5'
        vm_name = 'grh5k'
        self.service.get_virtual_machine = Mock()
        self.service.get_virtual_machine.return_value = None
        self.assertFalse(self.service.virtual_machine_exists(cs_name, dm_name, vm_name))
        self.service.get_virtual_machine.return_value = not None
        self.assertTrue(self.service.virtual_machine_exists(cs_name, dm_name, vm_name))
        self.service.get_virtual_machine.side_effect = Exception
        self.assertFalse(self.service.virtual_machine_exists(cs_name, dm_name, vm_name))

    def test_get_virtual_machine_network_config(self):
        cs_name = 'grtit3'
        dm_name = 'fdjhfr'
        vm_name = 'grt65g'
        self.service.get_virtual_machine = Mock()
        self.service.get_virtual_machine.return_value = None
        self.assertIsNone(self.service.get_virtual_machine_network_config(cs_name, dm_name, vm_name))
        c = ConfigurationSet()
        p = PersistentVMRole()
        p.configuration_sets.configuration_sets = [c]
        self.service.get_virtual_machine.return_value = p
        self.assertEqual(self.service.get_virtual_machine_network_config(cs_name, dm_name, vm_name), c)

    def test_get_assigned_endpoints(self):
        cs_name = 'dsfsd'
        self.service.get_hosted_service_properties = Mock()
        i = ConfigurationSetInputEndpoint('http', 'tcp', '80', '80')
        c = ConfigurationSet()
        c.input_endpoints.input_endpoints = [i]
        r = Role()
        r.configuration_sets.configuration_sets = [c]
        d = Deployment()
        d.role_list.roles = [r]
        h = HostedService()
        h.deployments.deployments = [d]
        self.service.get_hosted_service_properties.return_value = h
        self.assertEqual(len(self.service.get_assigned_endpoints(cs_name)), 1)

    def test_wait_for_async(self):
        r_id = 1
        sec = 1
        loop = 3
        self.service.get_operation_status = Mock()
        o = Operation()
        o.status = 'InProgress'
        self.service.get_operation_status.return_value = o
        self.assertFalse(self.service.wait_for_async(r_id, sec, loop))
        o.status = 'Succeeded'
        self.assertTrue(self.service.wait_for_async(r_id, sec, loop))
