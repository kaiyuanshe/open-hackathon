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

sys.path.append("..")
from hackathon.azureformation.utility import (
    find_unassigned_endpoints,
)
from azure.servicemanagement import (
    WindowsConfigurationSet,
    LinuxConfigurationSet,
    OSVirtualHardDisk,
    ConfigurationSet,
    ConfigurationSetInputEndpoint,
)
from threading import (
    current_thread,
)
from hackathon import Component
from hackathon.template import AZURE_UNIT


class TemplateUnit(Component):
    # template name in virtual_environment

    # other constants
    BLOB_BASE = '%s-%s-%s-%s-%s-%s-%s-%s.vhd'
    MEDIA_BASE = 'https://%s.%s/%s/%s'

    def __init__(self, virtual_environment):
        self.virtual_environment = virtual_environment

    def get_image_type(self):
        return self.virtual_environment[AZURE_UNIT.T_I][AZURE_UNIT.T_I_T]

    def is_vm_image(self):
        return self.get_image_type() == AZURE_UNIT.VM

    def get_vm_image_name(self):
        """
        Return None if image type is not vm
        :return:
        """
        return self.virtual_environment[AZURE_UNIT.T_I][AZURE_UNIT.T_I_N] if self.is_vm_image() else None

    def get_image_name(self):
        return self.virtual_environment[AZURE_UNIT.T_I][AZURE_UNIT.T_I_N]

    def get_system_config(self):
        """
        Return None if image type is vm
        :return:
        """
        if self.is_vm_image():
            return None
        sc = self.virtual_environment[AZURE_UNIT.T_SC]
        # check whether virtual machine is Windows or Linux
        if sc[AZURE_UNIT.T_SC_OF] == AZURE_UNIT.WINDOWS:
            system_config = WindowsConfigurationSet(computer_name=sc[AZURE_UNIT.T_SC_HN],
                                                    admin_password=sc[AZURE_UNIT.T_SC_UP],
                                                    admin_username=sc[AZURE_UNIT.T_SC_UN])
            system_config.domain_join = None
            system_config.win_rm = None
        else:
            system_config = LinuxConfigurationSet(host_name=sc[AZURE_UNIT.T_SC_HN],
                                                  user_name=sc[AZURE_UNIT.T_SC_UN],
                                                  user_password=sc[AZURE_UNIT.T_SC_UP],
                                                  disable_ssh_password_authentication=False)
        return system_config

    def get_os_virtual_hard_disk(self):
        """
        Return None if image type is vm
        Media link should be unique
        :return:
        """
        if self.is_vm_image():
            return None
        i = self.virtual_environment[AZURE_UNIT.T_I]
        sa = self.virtual_environment[AZURE_UNIT.T_SA]
        c = self.virtual_environment[AZURE_UNIT.T_C]
        now = self.util.get_now()
        blob = self.BLOB_BASE % (i[AZURE_UNIT.T_I_N],
                                 str(now.year),
                                 str(now.month),
                                 str(now.day),
                                 str(now.hour),
                                 str(now.minute),
                                 str(now.second),
                                 str(current_thread().ident))
        media_link = self.MEDIA_BASE % (sa[AZURE_UNIT.T_SA_SN],
                                        sa[AZURE_UNIT.T_SA_UB],
                                        c,
                                        blob)
        os_virtual_hard_disk = OSVirtualHardDisk(i[AZURE_UNIT.T_I_N], media_link)
        return os_virtual_hard_disk

    def get_network_config(self, service, update):
        """
        Return None if image type is vm and not update
        Public endpoint should be assigned in real time
        :param service:
        :return:
        """
        if self.is_vm_image() and not update:
            return None
        cs = self.virtual_environment[AZURE_UNIT.T_CS]
        nc = self.virtual_environment[AZURE_UNIT.T_NC]
        network_config = ConfigurationSet()
        network_config.configuration_set_type = nc[AZURE_UNIT.T_NC_CST]
        input_endpoints = nc[AZURE_UNIT.T_NC_IE]
        # avoid duplicate endpoint under same cloud service
        assigned_endpoints = service.get_assigned_endpoints(cs[AZURE_UNIT.T_CS_SN])
        endpoints = map(lambda i: i[AZURE_UNIT.T_NC_IE_LP], input_endpoints)
        unassigned_endpoints = map(str, find_unassigned_endpoints(endpoints, assigned_endpoints))
        map(lambda (i, u): i.update({AZURE_UNIT.T_NC_IE_PO: u}), zip(input_endpoints, unassigned_endpoints))
        for input_endpoint in input_endpoints:
            network_config.input_endpoints.input_endpoints.append(
                ConfigurationSetInputEndpoint(
                    input_endpoint[AZURE_UNIT.T_NC_IE_N],
                    input_endpoint[AZURE_UNIT.T_NC_IE_PR],
                    input_endpoint[AZURE_UNIT.T_NC_IE_PO],
                    input_endpoint[AZURE_UNIT.T_NC_IE_LP]
                )
            )
        return network_config

    def get_storage_account_name(self):
        return self.virtual_environment[AZURE_UNIT.T_SA][AZURE_UNIT.T_SA_SN]

    def get_storage_account_description(self):
        return self.virtual_environment[AZURE_UNIT.T_SA][AZURE_UNIT.T_SA_D]

    def get_storage_account_label(self):
        return self.virtual_environment[AZURE_UNIT.T_SA][AZURE_UNIT.T_SA_LA]

    def get_storage_account_location(self):
        return self.virtual_environment[AZURE_UNIT.T_SA][AZURE_UNIT.T_SA_LO]

    def get_cloud_service_name(self):
        return self.virtual_environment[AZURE_UNIT.T_CS][AZURE_UNIT.T_CS_SN]

    def get_cloud_service_label(self):
        return self.virtual_environment[AZURE_UNIT.T_CS][AZURE_UNIT.T_CS_LA]

    def get_cloud_service_location(self):
        return self.virtual_environment[AZURE_UNIT.T_CS][AZURE_UNIT.T_CS_LO]

    def get_deployment_slot(self):
        return self.virtual_environment[AZURE_UNIT.T_D][AZURE_UNIT.T_D_DS]

    def get_deployment_name(self):
        return self.virtual_environment[AZURE_UNIT.T_D][AZURE_UNIT.T_D_DN]

    def get_virtual_machine_name(self):
        return self.virtual_environment[AZURE_UNIT.T_RN]

    def get_virtual_machine_label(self):
        return self.virtual_environment[AZURE_UNIT.T_L]

    def get_virtual_machine_size(self):
        return self.virtual_environment[AZURE_UNIT.T_RS]

    def get_remote_provider_name(self):
        return self.virtual_environment[AZURE_UNIT.T_R][AZURE_UNIT.T_R_PROV]

    def get_remote_port_name(self):
        return self.virtual_environment[AZURE_UNIT.T_R][AZURE_UNIT.T_R_IEN]

    def get_remote_paras(self, name, hostname, port):
        r = self.virtual_environment[AZURE_UNIT.T_R]
        sc = self.virtual_environment[AZURE_UNIT.T_SC]
        remote = {
            AZURE_UNIT.RP_N: name,
            AZURE_UNIT.RP_DN: r[AZURE_UNIT.T_R_IEN],
            AZURE_UNIT.RP_HN: hostname,
            AZURE_UNIT.RP_PR: r[AZURE_UNIT.T_R_PROT],
            AZURE_UNIT.RP_PO: port,
            AZURE_UNIT.RP_UN: sc[AZURE_UNIT.T_SC_UN],
            AZURE_UNIT.RP_PA: sc[AZURE_UNIT.T_SC_UP],
            "enable-sftp": True
        }

        return remote
