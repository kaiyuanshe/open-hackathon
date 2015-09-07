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

from template_constants import UNIT, TEMPLATE


class DockerTemplateUnit(object):
    """
    Smallest unit in docker template
    """

    def __init__(self, dic):
        self.dic = self.load_default_config()
        for key, value in dic.iteritems():
            self.dic[key] = value

    def load_default_config(self):
        dic = {
            UNIT.NAME: 'web',
            UNIT.TYPE: 'ubuntu terminal',
            UNIT.DESCRIPTION: 'sample environment for ampcamp 2015',
            UNIT.PORTS: [
                {
                    UNIT.PORTS_NAME: 'Deploy',
                    UNIT.PORTS_PORT: 22,
                    UNIT.PORTS_PUBLIC: True,
                    UNIT.PORTS_PROTOCOL: 'tcp',
                }
            ],
            UNIT.REMOTE: {
                UNIT.REMOTE_PROVIDER: 'guacamole',
                UNIT.REMOTE_PROTOCOL: 'ssh',
                UNIT.REMOTE_USERNAME: 'root',
                UNIT.REMOTE_PASSWORD: 'root',
                UNIT.REMOTE_PORT: 22,
            },
            UNIT.HOSTNAME: '',
            UNIT.DOMAIN_NAME: '',
            UNIT.USER: '',
            UNIT.ATTACH_STDIN: False,
            UNIT.ATTACH_STDOUT: True,
            UNIT.ATTACH_STDERR: True,
            UNIT.TTY: True,
            UNIT.OPEN_STDIN: True,
            UNIT.STDIN_ONCE: True,
            UNIT.ENV: [],
            UNIT.CMD: [],
            UNIT.ENTRY_POINT: '',
            UNIT.IMAGE: '',
            UNIT.LABELS: {},
            UNIT.VOLUMES: {},
            UNIT.WORKING_DIR: '',
            UNIT.NETWORK_DISABLED: False,
            UNIT.EXPOSED_PORTS: {},
            UNIT.MAC_ADDRESS: '',
            UNIT.SECURITY_OPTS: [''],
            UNIT.HOST_CONFIG: {
                UNIT.HOST_CONFIG_BINDS: [],
                UNIT.HOST_CONFIG_LINKS: [],
                UNIT.HOST_CONFIG_LXC_CONF: {},
                UNIT.HOST_CONFIG_MEMORY: 0,
                UNIT.HOST_CONFIG_MEMORY_SWAP: 0,
                UNIT.HOST_CONFIG_CPU_SHARES: 0,
                UNIT.HOST_CONFIG_CPUSET_CPUS: '',
                UNIT.HOST_CONFIG_PORT_BINDING: {},
                UNIT.HOST_CONFIG_PUBLISH_ALL_PORTS: False,
                UNIT.HOST_CONFIG_PRIVILEGED: False,
                UNIT.HOST_CONFIG_READONLY_ROOTFS: False,
                UNIT.HOST_CONFIG_DNS: [],
                UNIT.HOST_CONFIG_DNS_SEARCH: [],
                UNIT.HOST_CONFIG_EXTRA_HOSTS: [],
                UNIT.HOST_CONFIG_VOLUMES_FROM: [],
                UNIT.HOST_CONFIG_CAP_ADD: [],
                UNIT.HOST_CONFIG_CAP_DROP: [],
                UNIT.HOST_CONFIG_RESTART_POLICY: {
                    UNIT.HOST_CONFIG_RESTART_POLICY_NAME: '',
                    UNIT.HOST_CONFIG_RESTART_POLICY_MAXIMUM_RETRY_COUNT: 0,
                },
                UNIT.HOST_CONFIG_NETWORK_MODE: '',
                UNIT.HOST_CONFIG_DEVICES: [],
                UNIT.HOST_CONFIG_ULIMITS: [],
                UNIT.HOST_CONFIG_LOG_CONFIG: {
                    UNIT.HOST_CONFIG_LOG_CONFIG_TYPE: 'json-file',
                    UNIT.HOST_CONFIG_LOG_CONFIG_CONFIG: {},
                },
                UNIT.HOST_CONFIG_CGROUP_PARENT: '',
            },
        }
        return dic

    def set_name(self, name):
        self.dic[UNIT.NAME] = name

    def get_name(self):
        return self.dic[UNIT.NAME]

    def get_container_config(self):
        """
        Compose post data for docker remote api create
        :return:
        """
        for p in self.dic[UNIT.PORTS]:
            key = '%d/%s' % (p[UNIT.PORTS_PORT], p[UNIT.PORTS_PROTOCOL])
            self.dic[UNIT.EXPOSED_PORTS][key] = {}
            self.dic[UNIT.HOST_CONFIG][UNIT.HOST_CONFIG_PORT_BINDING][key] = \
                [{UNIT.HOST_CONFIG_HOST_IP: '', UNIT.HOST_CONFIG_HOST_PORT: str(p[UNIT.PORTS_HOST_PORT])}]
        self.dic.pop(UNIT.NAME, "")
        self.dic.pop(UNIT.TYPE, "")
        self.dic.pop(UNIT.DESCRIPTION, "")
        self.dic.pop(UNIT.PORTS, None)
        self.dic.pop(UNIT.REMOTE, None)
        self.dic.pop(TEMPLATE.VIRTUAL_ENVIRONMENTS_PROVIDER)
        return self.dic

    def get_image_with_tag(self):
        return self.dic[UNIT.IMAGE]

    def get_ports(self):
        return self.dic[UNIT.PORTS]

    def get_remote(self):
        return self.dic[UNIT.REMOTE]

    def get_image_without_tag(self):
        image = self.get_image_with_tag()
        return image.split(':')[0]

    def get_tag(self):
        image = self.get_image_with_tag()
        data = image.split(':')
        if len(data) == 2:
            return data[1]
        else:
            return 'latest'

    def get_run_command(self):
        cmd = self.dic[UNIT.CMD]
        if cmd:
            return " ".join(cmd)
        return ""

    def get_instance_env_vars(self):
        env_vars = {}

        def convert(env):
            arr = env.split("=")
            if len(arr) == 2:
                env_vars[arr[0]] = arr[1]

        map(lambda env: convert(env), UNIT.ENV or [])
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

        map(lambda p: convert(p), self.dic[UNIT.PORTS])
        return instance_ports
