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
import datetime


class TemplateUnit:
    # template name in virtual_environment
    T_P = 'provider'
    T_SA = 'storage_account'
    T_SA_SN = 'service_name'
    T_SA_D = 'description'
    T_SA_LA = 'label'
    T_SA_LO = 'location'
    T_SA_UB = 'url_base'
    T_C = 'container'
    T_CS = 'cloud_service'
    T_CS_SN = 'service_name'
    T_CS_LA = 'label'
    T_CS_LO = 'location'
    T_D = 'deployment'
    T_D_DN = 'deployment_name'
    T_D_DS = 'deployment_slot'
    T_L = 'label'
    T_RN = 'role_name'
    T_I = 'image'
    T_I_T = 'type'
    T_I_N = 'name'
    T_SC = 'system_config'
    T_SC_OF = 'os_family'
    T_SC_HN = 'host_name'
    T_SC_UN = 'user_name'
    T_SC_UP = 'user_password'
    T_NC = 'network_config'
    T_NC_CST = 'configuration_set_type'
    T_NC_IE = 'input_endpoints'
    T_NC_IE_N = 'name'
    T_NC_IE_PR = 'protocol'
    T_NC_IE_LP = 'local_port'
    T_NC_IE_PO = 'port'
    T_R = 'remote'
    T_R_PROV = 'provider'
    T_R_PROT = 'protocol'
    T_R_IEN = 'input_endpoint_name'
    T_RS = 'role_size'
    # image type name
    OS = 'os'
    VM = 'vm'
    # os family name
    WINDOWS = 'Windows'
    LINUX = 'Linux'
    # remote parameter name
    RP_N = 'name'
    RP_DN = 'displayname'
    RP_HN = 'hostname'
    RP_PR = 'protocol'
    RP_PO = 'port'
    RP_UN = 'username'
    RP_PA = 'password'
    # other constants
    BLOB_BASE = '%s-%s-%s-%s-%s-%s-%s-%s.vhd'
    MEDIA_BASE = 'https://%s.%s/%s/%s'

    def __init__(self, virtual_environment):
        self.virtual_environment = virtual_environment

    def get_image_type(self):
        return self.virtual_environment[self.T_I][self.T_I_T]

    def is_vm_image(self):
        return self.get_image_type() == self.VM

    def get_vm_image_name(self):
        """
        Return None if image type is not vm
        :return:
        """
        return self.virtual_environment[self.T_I][self.T_I_N] if self.is_vm_image() else None

    def get_image_name(self):
        return self.virtual_environment[self.T_I][self.T_I_N]

    def get_system_config(self):
        """
        Return None if image type is vm
        :return:
        """
        if self.is_vm_image():
            return None
        sc = self.virtual_environment[self.T_SC]
        # check whether virtual machine is Windows or Linux
        if sc[self.T_SC_OF] == self.WINDOWS:
            system_config = WindowsConfigurationSet(computer_name=sc[self.T_SC_HN],
                                                    admin_password=sc[self.T_SC_UP],
                                                    admin_username=sc[self.T_SC_UN])
            system_config.domain_join = None
            system_config.win_rm = None
        else:
            system_config = LinuxConfigurationSet(host_name=sc[self.T_SC_HN],
                                                  user_name=sc[self.T_SC_UN],
                                                  user_password=sc[self.T_SC_UP],
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
        i = self.virtual_environment[self.T_I]
        sa = self.virtual_environment[self.T_SA]
        c = self.virtual_environment[self.T_C]
        now = datetime.datetime.now()
        blob = self.BLOB_BASE % (i[self.T_I_N],
                                 str(now.year),
                                 str(now.month),
                                 str(now.day),
                                 str(now.hour),
                                 str(now.minute),
                                 str(now.second),
                                 str(current_thread().ident))
        media_link = self.MEDIA_BASE % (sa[self.T_SA_SN],
                                        sa[self.T_SA_UB],
                                        c,
                                        blob)
        os_virtual_hard_disk = OSVirtualHardDisk(i[self.T_I_N], media_link)
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
        cs = self.virtual_environment[self.T_CS]
        nc = self.virtual_environment[self.T_NC]
        network_config = ConfigurationSet()
        network_config.configuration_set_type = nc[self.T_NC_CST]
        input_endpoints = nc[self.T_NC_IE]
        # avoid duplicate endpoint under same cloud service
        assigned_endpoints = service.get_assigned_endpoints(cs[self.T_CS_SN])
        endpoints = map(lambda i: i[self.T_NC_IE_LP], input_endpoints)
        unassigned_endpoints = map(str, find_unassigned_endpoints(endpoints, assigned_endpoints))
        map(lambda (i, u): i.update({self.T_NC_IE_PO: u}), zip(input_endpoints, unassigned_endpoints))
        for input_endpoint in input_endpoints:
            network_config.input_endpoints.input_endpoints.append(
                ConfigurationSetInputEndpoint(
                    input_endpoint[self.T_NC_IE_N],
                    input_endpoint[self.T_NC_IE_PR],
                    input_endpoint[self.T_NC_IE_PO],
                    input_endpoint[self.T_NC_IE_LP]
                )
            )
        return network_config

    def get_storage_account_name(self):
        return self.virtual_environment[self.T_SA][self.T_SA_SN]

    def get_storage_account_description(self):
        return self.virtual_environment[self.T_SA][self.T_SA_D]

    def get_storage_account_label(self):
        return self.virtual_environment[self.T_SA][self.T_SA_LA]

    def get_storage_account_location(self):
        return self.virtual_environment[self.T_SA][self.T_SA_LO]

    def get_cloud_service_name(self):
        return self.virtual_environment[self.T_CS][self.T_CS_SN]

    def get_cloud_service_label(self):
        return self.virtual_environment[self.T_CS][self.T_CS_LA]

    def get_cloud_service_location(self):
        return self.virtual_environment[self.T_CS][self.T_CS_LO]

    def get_deployment_slot(self):
        return self.virtual_environment[self.T_D][self.T_D_DS]

    def get_deployment_name(self):
        return self.virtual_environment[self.T_D][self.T_D_DN]

    def get_virtual_machine_name(self):
        return self.virtual_environment[self.T_RN]

    def get_virtual_machine_label(self):
        return self.virtual_environment[self.T_L]

    def get_virtual_machine_size(self):
        return self.virtual_environment[self.T_RS]

    def get_remote_provider_name(self):
        return self.virtual_environment[self.T_R][self.T_R_PROV]

    def get_remote_port_name(self):
        return self.virtual_environment[self.T_R][self.T_R_IEN]

    def get_remote_paras(self, name, hostname, port):
        r = self.virtual_environment[self.T_R]
        sc = self.virtual_environment[self.T_SC]
        remote = {
            self.RP_N: name,
            self.RP_DN: r[self.T_R_IEN],
            self.RP_HN: hostname,
            self.RP_PR: r[self.T_R_PROT],
            self.RP_PO: port,
            self.RP_UN: sc[self.T_SC_UN],
            self.RP_PA: sc[self.T_SC_UP]
        }
        return remote