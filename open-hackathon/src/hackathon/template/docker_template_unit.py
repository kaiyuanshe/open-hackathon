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


class DockerTemplateUnit(object):
    """
    Smallest unit in docker template
    """
    T_N = 'name'
    T_P = 'ports'
    T_P_N = 'name'
    T_P_PO = 'port'
    T_P_PU = 'public'
    T_P_PR = 'protocol'
    T_P_U = 'url'
    T_R = 'remote'
    T_R_PROV = 'provider'
    T_R_PROT = 'protocol'
    T_R_U = 'username'
    T_R_PA = 'password'
    T_R_PO = 'port'
    T_H = 'Hostname'
    T_D = 'Domainname'
    T_U = 'User'
    T_ASI = 'AttachStdin'
    T_ASO = 'AttachStdout'
    T_ASE = 'AttachStderr'
    T_T = 'Tty'
    T_OS = 'OpenStdin'
    T_SO = 'StdinOnce'
    T_E = 'Env'
    T_C = 'Cmd'
    T_EP = 'Entrypoint'
    T_I = 'Image'
    T_L = 'Labels'
    T_V = 'Volumes'
    T_WD = 'WorkingDir'
    T_ND = 'NetworkDisabled'
    T_MA = 'MacAddress'
    T_SOP = 'SecurityOpts'
    T_HC = 'HostConfig'
    T_HC_B = 'Binds'
    T_HC_L = 'Links'
    T_HC_LC = 'LxcConf'
    T_HC_M = 'Memory'
    T_HC_MS = 'MemorySwap'
    T_HC_CS = 'CpuShares'
    T_HC_CC = 'CpusetCpus'
    T_HC_PB = 'PortBindings'
    T_HC_PAP = 'PublishAllPorts'
    T_HC_P = 'Privileged'
    T_HC_RR = 'ReadonlyRootfs'
    T_HC_D = 'Dns'
    T_HC_DS = 'DnsSearch'
    T_HC_EH = 'ExtraHosts'
    T_HC_VF = 'VolumesFrom'
    T_HC_CA = 'CapAdd'
    T_HC_CD = 'CapDrop'
    T_HC_RP = 'RestartPolicy'
    T_HC_RP_N = 'Name'
    T_HC_RP_MRC = 'MaximumRetryCount'
    T_HC_NM = 'NetworkMode'
    T_HC_DE = 'Devices'
    T_HC_U = 'Ulimits'
    T_HC_LCO = 'LogConfig'
    T_HC_LCO_T = 'Type'
    T_HC_LCO_C = 'Config'
    T_HC_CP = 'CgroupParent'

    def __init__(self, dic):
        self.dic = self.load_default_config()
        for key, value in dic.iteritems():
            self.dic[key] = value

    def load_default_config(self):
        dic = {
            self.T_N: 'web',
            self.T_P: [
                {
                    self.T_P_N: 'Tachyon',
                    self.T_P_PO: 19999,
                    self.T_P_PU: True,
                    self.T_P_PR: 'tcp',
                    self.T_P_U: 'http://{0}:{1}',
                },
                {
                    self.T_P_N: 'Deploy',
                    self.T_P_PO: 22,
                    self.T_P_PU: True,
                    self.T_P_PR: 'tcp',
                },
                {
                    self.T_P_N: 'WebUI',
                    self.T_P_PO: 4040,
                    self.T_P_PU: True,
                    self.T_P_PR: 'tcp',
                    self.T_P_U: 'http://{0}:{1}'
                },
            ],
            self.T_R: {
                self.T_R_PROV: 'guacamole',
                self.T_R_PROT: 'ssh',
                self.T_R_U: 'root',
                self.T_R_PA: 'root',
                self.T_R_PO: 22,
            },
            self.T_H: '',
            self.T_D: '',
            self.T_U: '',
            self.T_ASI: False,
            self.T_ASO: True,
            self.T_ASE: True,
            self.T_T: True,
            self.T_OS: True,
            self.T_SO: True,
            self.T_E: ['JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/jre/'],
            self.T_C: ['/usr/sbin/sshd', '-D'],
            self.T_EP: '',
            self.T_I: 'sffamily/ampcamp5:v5',
            self.T_L: {},
            self.T_V: {},
            self.T_WD: '',
            self.T_ND: False,
            self.T_MA: '',
            self.T_SOP: [''],
            self.T_HC: {
                self.T_HC_B: [],
                self.T_HC_L: [],
                self.T_HC_LC: {},
                self.T_HC_M: 0,
                self.T_HC_MS: 0,
                self.T_HC_CS: 0,
                self.T_HC_CC: '',
                self.T_HC_PB: {},
                self.T_HC_PAP: False,
                self.T_HC_P: False,
                self.T_HC_RR: False,
                self.T_HC_D: [],
                self.T_HC_DS: [],
                self.T_HC_EH: [],
                self.T_HC_VF: [],
                self.T_HC_CA: [],
                self.T_HC_CD: [],
                self.T_HC_RP: {
                    self.T_HC_RP_N: '',
                    self.T_HC_RP_MRC: 0,
                },
                self.T_HC_NM: '',
                self.T_HC_DE: [],
                self.T_HC_U: [],
                self.T_HC_LCO: {
                    self.T_HC_LCO_T: 'json-file',
                    self.T_HC_LCO_C: {},
                },
                self.T_HC_CP: '',
            },
        }
        return dic

    def set_name(self, name):
        """
        Set name as generated unique name
        :param name:
        :return:
        """
        self.dic[self.T_N] = name

    def get_name(self):
        return self.dic[self.T_N]

    def get_container_config(self):
        """
        Compose post data for docker remote api create
        :return:
        """
        raise NotImplementedError