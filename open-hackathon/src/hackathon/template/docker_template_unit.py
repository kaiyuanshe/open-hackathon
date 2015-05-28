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
from hackathon.template.base_template import (
    BaseTemplate,
)


class DockerTemplateUnit(object):
    """
    Smallest unit in docker template
    """
    NAME = 'name'
    PORTS = 'ports'
    PORTS_NAME = 'name'
    PORTS_PORT = 'port'
    PORTS_PUBLIC = 'public'
    PORTS_PROTOCOL = 'protocol'
    PORTS_URL = 'url'
    PORTS_HOST_PORT = 'host_port'
    PORTS_PUBLIC_PORT = 'public_port'
    REMOTE = 'remote'
    REMOTE_PROVIDER = 'provider'
    REMOTE_PROTOCOL = 'protocol'
    REMOTE_USERNAME = 'username'
    REMOTE_PASSWORD = 'password'
    REMOTE_PORT = 'port'
    HOSTNAME = 'Hostname'
    DOMAIN_NAME = 'Domainname'
    USER = 'User'
    ATTACH_STDIN = 'AttachStdin'
    ATTACH_STDOUT = 'AttachStdout'
    ATTACH_STDERR = 'AttachStderr'
    TTY = 'Tty'
    OPEN_STDIN = 'OpenStdin'
    STDIN_ONCE = 'StdinOnce'
    ENV = 'Env'
    CMD = 'Cmd'
    ENTRY_POINT = 'Entrypoint'
    IMAGE = 'Image'
    LABELS = 'Labels'
    VOLUMES = 'Volumes'
    WORKING_DIR = 'WorkingDir'
    NETWORK_DISABLED = 'NetworkDisabled'
    EXPOSED_PORTS = 'ExposedPorts'
    MAC_ADDRESS = 'MacAddress'
    SECURITY_OPTS = 'SecurityOpts'
    HOST_CONFIG = 'HostConfig'
    HOST_CONFIG_BINDS = 'Binds'
    HOST_CONFIG_LINKS = 'Links'
    HOST_CONFIG_LXC_CONF = 'LxcConf'
    HOST_CONFIG_MEMORY = 'Memory'
    HOST_CONFIG_MEMORY_SWAP = 'MemorySwap'
    HOST_CONFIG_CPU_SHARES = 'CpuShares'
    HOST_CONFIG_CPUSET_CPUS = 'CpusetCpus'
    HOST_CONFIG_PORT_BINDING = 'PortBindings'
    HOST_CONFIG_HOST_IP = 'HostIp'
    HOST_CONFIG_HOST_PORT = 'HostPort'
    HOST_CONFIG_PUBLISH_ALL_PORTS = 'PublishAllPorts'
    HOST_CONFIG_PRIVILEGED = 'Privileged'
    HOST_CONFIG_READONLY_ROOTFS = 'ReadonlyRootfs'
    HOST_CONFIG_DNS = 'Dns'
    HOST_CONFIG_DNS_SEARCH = 'DnsSearch'
    HOST_CONFIG_EXTRA_HOSTS = 'ExtraHosts'
    HOST_CONFIG_VOLUMES_FROM = 'VolumesFrom'
    HOST_CONFIG_CAP_ADD = 'CapAdd'
    HOST_CONFIG_CAP_DROP = 'CapDrop'
    HOST_CONFIG_RESTART_POLICY = 'RestartPolicy'
    HOST_CONFIG_RESTART_POLICY_NAME = 'Name'
    HOST_CONFIG_RESTART_POLICY_MAXIMUM_RETRY_COUNT = 'MaximumRetryCount'
    HOST_CONFIG_NETWORK_MODE = 'NetworkMode'
    HOST_CONFIG_DEVICES = 'Devices'
    HOST_CONFIG_ULIMITS = 'Ulimits'
    HOST_CONFIG_LOG_CONFIG = 'LogConfig'
    HOST_CONFIG_LOG_CONFIG_TYPE = 'Type'
    HOST_CONFIG_LOG_CONFIG_CONFIG = 'Config'
    HOST_CONFIG_CGROUP_PARENT = 'CgroupParent'

    def __init__(self, dic):
        self.dic = self.load_default_config()
        for key, value in dic.iteritems():
            self.dic[key] = value

    def load_default_config(self):
        dic = {
            self.NAME: 'web',
            self.PORTS: [
                {
                    self.PORTS_NAME: 'Tachyon',
                    self.PORTS_PORT: 19999,
                    self.PORTS_PUBLIC: True,
                    self.PORTS_PROTOCOL: 'tcp',
                    self.PORTS_URL: 'http://{0}:{1}',
                },
                {
                    self.PORTS_NAME: 'Deploy',
                    self.PORTS_PORT: 22,
                    self.PORTS_PUBLIC: True,
                    self.PORTS_PROTOCOL: 'tcp',
                },
                {
                    self.PORTS_NAME: 'WebUI',
                    self.PORTS_PORT: 4040,
                    self.PORTS_PUBLIC: True,
                    self.PORTS_PROTOCOL: 'tcp',
                    self.PORTS_URL: 'http://{0}:{1}'
                },
            ],
            self.REMOTE: {
                self.REMOTE_PROVIDER: 'guacamole',
                self.REMOTE_PROTOCOL: 'ssh',
                self.REMOTE_USERNAME: 'root',
                self.REMOTE_PASSWORD: 'root',
                self.REMOTE_PORT: 22,
            },
            self.HOSTNAME: '',
            self.DOMAIN_NAME: '',
            self.USER: '',
            self.ATTACH_STDIN: False,
            self.ATTACH_STDOUT: True,
            self.ATTACH_STDERR: True,
            self.TTY: True,
            self.OPEN_STDIN: True,
            self.STDIN_ONCE: True,
            self.ENV: ['JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/jre/'],
            self.CMD: ['/usr/sbin/sshd', '-D'],
            self.ENTRY_POINT: '',
            self.IMAGE: 'sffamily/ampcamp5:v5',
            self.LABELS: {},
            self.VOLUMES: {},
            self.WORKING_DIR: '',
            self.NETWORK_DISABLED: False,
            self.EXPOSED_PORTS: {},
            self.MAC_ADDRESS: '',
            self.SECURITY_OPTS: [''],
            self.HOST_CONFIG: {
                self.HOST_CONFIG_BINDS: [],
                self.HOST_CONFIG_LINKS: [],
                self.HOST_CONFIG_LXC_CONF: {},
                self.HOST_CONFIG_MEMORY: 0,
                self.HOST_CONFIG_MEMORY_SWAP: 0,
                self.HOST_CONFIG_CPU_SHARES: 0,
                self.HOST_CONFIG_CPUSET_CPUS: '',
                self.HOST_CONFIG_PORT_BINDING: {},
                self.HOST_CONFIG_PUBLISH_ALL_PORTS: False,
                self.HOST_CONFIG_PRIVILEGED: False,
                self.HOST_CONFIG_READONLY_ROOTFS: False,
                self.HOST_CONFIG_DNS: [],
                self.HOST_CONFIG_DNS_SEARCH: [],
                self.HOST_CONFIG_EXTRA_HOSTS: [],
                self.HOST_CONFIG_VOLUMES_FROM: [],
                self.HOST_CONFIG_CAP_ADD: [],
                self.HOST_CONFIG_CAP_DROP: [],
                self.HOST_CONFIG_RESTART_POLICY: {
                    self.HOST_CONFIG_RESTART_POLICY_NAME: '',
                    self.HOST_CONFIG_RESTART_POLICY_MAXIMUM_RETRY_COUNT: 0,
                },
                self.HOST_CONFIG_NETWORK_MODE: '',
                self.HOST_CONFIG_DEVICES: [],
                self.HOST_CONFIG_ULIMITS: [],
                self.HOST_CONFIG_LOG_CONFIG: {
                    self.HOST_CONFIG_LOG_CONFIG_TYPE: 'json-file',
                    self.HOST_CONFIG_LOG_CONFIG_CONFIG: {},
                },
                self.HOST_CONFIG_CGROUP_PARENT: '',
            },
        }
        return dic

    def set_name(self, name):
        self.dic[self.NAME] = name

    def get_name(self):
        return self.dic[self.NAME]

    def get_container_config(self):
        """
        Compose post data for docker remote api create
        :return:
        """
        for p in self.dic[self.PORTS]:
            key = '%d/%s' % (p[self.PORTS_PORT], p[self.PORTS_PROTOCOL])
            self.dic[self.EXPOSED_PORTS][key] = {}
            self.dic[self.HOST_CONFIG][self.HOST_CONFIG_PORT_BINDING][key] = \
                [{self.HOST_CONFIG_HOST_IP: '', self.HOST_CONFIG_HOST_PORT: str(p[self.PORTS_HOST_PORT])}]
        self.dic.pop(self.NAME)
        self.dic.pop(self.PORTS)
        self.dic.pop(self.REMOTE)
        self.dic.pop(BaseTemplate.VIRTUAL_ENVIRONMENTS_PROVIDER)
        return self.dic

    def get_image(self):
        return self.dic[self.IMAGE]

    def get_ports(self):
        return self.dic[self.PORTS]

    def get_remote(self):
        return self.dic[self.REMOTE]