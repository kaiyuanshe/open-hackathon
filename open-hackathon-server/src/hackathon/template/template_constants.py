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

"""constants used in template files"""


class TEMPLATE:
    """constants in template level"""
    TEMPLATE_NAME = 'name'
    DESCRIPTION = 'description'
    VIRTUAL_ENVIRONMENTS = 'virtual_environments'
    VIRTUAL_ENVIRONMENT_PROVIDER = "provider"

class DOCKER_UNIT:
    """constants in docker virtual_environment in template"""
    NAME = 'name'
    TYPE = 'type'
    DESCRIPTION = 'description'
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


class AZURE_UNIT:
    """constants for azure virtual_environment in template file"""
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
