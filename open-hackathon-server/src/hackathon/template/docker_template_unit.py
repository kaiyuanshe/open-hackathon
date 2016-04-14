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

from template_constants import DOCKER_UNIT
from template_unit import TemplateUnit
from hackathon.constants import VE_PROVIDER

__all__ = ["DockerTemplateUnit"]


class DockerTemplateUnit(TemplateUnit):
    """
    Smallest unit in docker template
    """

    def __init__(self, dic):
        super(DockerTemplateUnit, self).__init__(VE_PROVIDER.DOCKER)
        self.dic = self.load_default_config()
        for key, value in dic.iteritems():
            self.dic[key] = value

    def load_default_config(self):
        dic = {
            DOCKER_UNIT.NAME: 'docker',
            DOCKER_UNIT.TYPE: 'ubuntu terminal',
            DOCKER_UNIT.DESCRIPTION: '',
            DOCKER_UNIT.PORTS: [
                {
                    DOCKER_UNIT.PORTS_NAME: 'Deploy',
                    DOCKER_UNIT.PORTS_PORT: 22,
                    DOCKER_UNIT.PORTS_PUBLIC: True,
                    DOCKER_UNIT.PORTS_PROTOCOL: 'tcp',
                }
            ],
            DOCKER_UNIT.REMOTE: {
                DOCKER_UNIT.REMOTE_PROVIDER: 'guacamole',
                DOCKER_UNIT.REMOTE_PROTOCOL: 'ssh',
                DOCKER_UNIT.REMOTE_USERNAME: 'root',
                DOCKER_UNIT.REMOTE_PASSWORD: 'root',
                DOCKER_UNIT.REMOTE_PORT: 22,
            },
            DOCKER_UNIT.HOSTNAME: '',
            DOCKER_UNIT.DOMAIN_NAME: '',
            DOCKER_UNIT.USER: '',
            DOCKER_UNIT.ATTACH_STDIN: False,
            DOCKER_UNIT.ATTACH_STDOUT: True,
            DOCKER_UNIT.ATTACH_STDERR: True,
            DOCKER_UNIT.TTY: True,
            DOCKER_UNIT.OPEN_STDIN: True,
            DOCKER_UNIT.STDIN_ONCE: True,
            DOCKER_UNIT.ENV: [],
            DOCKER_UNIT.CMD: [],
            DOCKER_UNIT.ENTRY_POINT: '',
            DOCKER_UNIT.IMAGE: '',
            DOCKER_UNIT.LABELS: {},
            DOCKER_UNIT.VOLUMES: {},
            DOCKER_UNIT.WORKING_DIR: '',
            DOCKER_UNIT.NETWORK_DISABLED: False,
            DOCKER_UNIT.EXPOSED_PORTS: {},
            DOCKER_UNIT.MAC_ADDRESS: '',
            DOCKER_UNIT.SECURITY_OPTS: [''],
            DOCKER_UNIT.HOST_CONFIG: {
                DOCKER_UNIT.HOST_CONFIG_BINDS: [],
                DOCKER_UNIT.HOST_CONFIG_LINKS: [],
                DOCKER_UNIT.HOST_CONFIG_LXC_CONF: {},
                DOCKER_UNIT.HOST_CONFIG_MEMORY: 0,
                DOCKER_UNIT.HOST_CONFIG_MEMORY_SWAP: 0,
                DOCKER_UNIT.HOST_CONFIG_CPU_SHARES: 0,
                DOCKER_UNIT.HOST_CONFIG_CPUSET_CPUS: '',
                DOCKER_UNIT.HOST_CONFIG_PORT_BINDING: {},
                DOCKER_UNIT.HOST_CONFIG_PUBLISH_ALL_PORTS: False,
                DOCKER_UNIT.HOST_CONFIG_PRIVILEGED: False,
                DOCKER_UNIT.HOST_CONFIG_READONLY_ROOTFS: False,
                DOCKER_UNIT.HOST_CONFIG_DNS: [],
                DOCKER_UNIT.HOST_CONFIG_DNS_SEARCH: [],
                DOCKER_UNIT.HOST_CONFIG_EXTRA_HOSTS: [],
                DOCKER_UNIT.HOST_CONFIG_VOLUMES_FROM: [],
                DOCKER_UNIT.HOST_CONFIG_CAP_ADD: [],
                DOCKER_UNIT.HOST_CONFIG_CAP_DROP: [],
                DOCKER_UNIT.HOST_CONFIG_RESTART_POLICY: {
                    DOCKER_UNIT.HOST_CONFIG_RESTART_POLICY_NAME: '',
                    DOCKER_UNIT.HOST_CONFIG_RESTART_POLICY_MAXIMUM_RETRY_COUNT: 0,
                },
                DOCKER_UNIT.HOST_CONFIG_NETWORK_MODE: '',
                DOCKER_UNIT.HOST_CONFIG_DEVICES: [],
                DOCKER_UNIT.HOST_CONFIG_ULIMITS: [],
                DOCKER_UNIT.HOST_CONFIG_LOG_CONFIG: {
                    DOCKER_UNIT.HOST_CONFIG_LOG_CONFIG_TYPE: 'json-file',
                    DOCKER_UNIT.HOST_CONFIG_LOG_CONFIG_CONFIG: {},
                },
                DOCKER_UNIT.HOST_CONFIG_CGROUP_PARENT: '',
            },
        }
        return dic

    def set_name(self, name):
        self.dic[DOCKER_UNIT.NAME] = name

    def get_name(self):
        return self.dic[DOCKER_UNIT.NAME]

    def get_type(self):
        return self.dic[DOCKER_UNIT.TYPE]

    def get_description(self):
        return self.dic[DOCKER_UNIT.DESCRIPTION]

    def get_container_config(self):
        """
        Compose post data for docker remote api create
        :return:
        """
        for p in self.dic[DOCKER_UNIT.PORTS]:
            key = '%d/%s' % (p[DOCKER_UNIT.PORTS_PORT], p[DOCKER_UNIT.PORTS_PROTOCOL])
            self.dic[DOCKER_UNIT.EXPOSED_PORTS][key] = {}
            self.dic[DOCKER_UNIT.HOST_CONFIG][DOCKER_UNIT.HOST_CONFIG_PORT_BINDING][key] = \
                [{DOCKER_UNIT.HOST_CONFIG_HOST_IP: '',
                  DOCKER_UNIT.HOST_CONFIG_HOST_PORT: str(p[DOCKER_UNIT.PORTS_HOST_PORT])}]
        self.dic.pop(DOCKER_UNIT.NAME, "")
        self.dic.pop(DOCKER_UNIT.TYPE, "")
        self.dic.pop(DOCKER_UNIT.PROVIDER, "")
        self.dic.pop(DOCKER_UNIT.DESCRIPTION, "")
        self.dic.pop(DOCKER_UNIT.PORTS, None)
        self.dic.pop(DOCKER_UNIT.REMOTE, None)
        if not self.dic[DOCKER_UNIT.CMD]:
            self.dic.pop(DOCKER_UNIT.CMD, [])
        if not self.dic[DOCKER_UNIT.ENTRY_POINT]:
            self.dic.pop(DOCKER_UNIT.ENTRY_POINT, "")
        return self.dic

    def get_image_with_tag(self):
        image = self.dic[DOCKER_UNIT.IMAGE]
        data = image.split(':')
        if len(data) == 2:
            return image
        else:
            return image + ':latest'

    def set_ports(self, port_cfg):
        self.dic[DOCKER_UNIT.PORTS] = port_cfg

    def get_ports(self):
        return self.dic[DOCKER_UNIT.PORTS]

    def get_remote(self):
        return self.dic[DOCKER_UNIT.REMOTE]

    def get_image_without_tag(self):
        image = self.get_image_with_tag()
        return image.split(':')[0]

    def get_tag(self):
        image = self.get_image_with_tag()
        return image.split(':')[1]

    def get_run_command(self):
        cmd = self.dic[DOCKER_UNIT.CMD]
        if cmd:
            return " ".join(cmd)
        return ""

    def get_instance_env_vars(self):
        env_vars = {}

        def convert(env):
            arr = env.split("=")
            if len(arr) == 2:
                env_vars[arr[0]] = arr[1]

        map(lambda env: convert(env), self.dic[DOCKER_UNIT.ENV] or [])
        return env_vars

    def get_instance_ports(self):
        instance_ports = []

        def convert(p):
            instance_ports.append({
                "container_port": p["port"],
                "protocol": p["protocol"] or "tcp",
                # endpoint_type: "tcp-endpoint" or "direct-endpoint"? not sure the meanings or usages. Communicating...
                "endpoint_type": "tcp-endpoint"
            })

        map(lambda p: convert(p), self.dic[DOCKER_UNIT.PORTS])
        return instance_ports
