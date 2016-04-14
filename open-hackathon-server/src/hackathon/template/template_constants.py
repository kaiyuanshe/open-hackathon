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
    PROVIDER = 'provider'
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
    STORAGE_ACCOUNT = 'storage_account'
    STORAGE_ACCOUNT_SERVICE_NAME = 'service_name'
    STORAGE_ACCOUNT_DESCRIPTION = 'description'
    STORAGE_ACCOUNT_LABEL = 'label'
    STORAGE_ACCOUNT_LOCATION = 'location'
    STORAGE_ACCOUNT_URL_BASE = 'url_base'

    CONTAINER = 'container'

    CLOUD_SERVICE = 'cloud_service'
    CLOUD_SERVICE_SERVICE_NAME = 'service_name'
    CLOUD_SERVICE_LABEL = 'label'
    CLOUD_SERVICE_LOCATION = 'location'

    DEPLOYMENT = 'deployment'
    DEPLOYMENT_DEPLOYMENT_NAME = 'deployment_name'
    DEPLOYMENT_DEPLOYMENT_SLOT = 'deployment_slot'

    LABEL = 'label'
    ROLE_NAME = 'role_name'
    ROLE_SIZE = 'role_size'

    IMAGE = 'image'
    IMAGE_TYPE = 'type'
    IMAGE_NAME = 'name'

    SYSTEM_CONFIG = 'system_config'
    SYSTEM_CONFIG_OS_FAMILY = 'os_family'
    SYSTEM_CONFIG_HOST_NAME = 'host_name'
    SYSTEM_CONFIG_USER_NAME = 'user_name'
    SYSTEM_CONFIG_USER_PASSWORD = 'user_password'

    NETWORK_CONFIG = 'network_config'
    NETWORK_CONFIG_CONFIGURATION_SET_TYPE = 'configuration_set_type'
    NETWORK_CONFIG_INPUT_ENDPOINTS = 'input_endpoints'
    NETWORK_CONFIG_INPUT_ENDPOINTS_NAME = 'name'
    NETWORK_CONFIG_INPUT_ENDPOINTS_PROTOCOL = 'protocol'
    NETWORK_CONFIG_INPUT_ENDPOINTS_LOCAL_PORT = 'local_port'
    NETWORK_CONFIG_INPUT_ENDPOINTS_PORT = 'port'
    NETWORK_CONFIG_INPUT_ENDPOINTS_URL = 'url'

    REMOTE = 'remote'
    REMOTE_PROVIDER = 'provider'
    REMOTE_PROTOCOL = 'protocol'
    REMOTE_INPUT_ENDPOINT_NAME = 'input_endpoint_name'

    # image type name
    OS = 'os'
    VM = 'vm'

    # os family name
    WINDOWS = 'Windows'
    LINUX = 'Linux'

    # remote parameter name
    REMOTE_PARAMETER_NAME = 'name'
    REMOTE_PARAMETER_DISPLAY_NAME = 'displayname'
    REMOTE_PARAMETER_HOST_NAME = 'hostname'
    REMOTE_PARAMETER_PROTOCOL = 'protocol'
    REMOTE_PARAMETER_PORT = 'port'
    REMOTE_PARAMETER_USER_NAME = 'username'
    REMOTE_PARAMETER_PASSWORD = 'password'

    RESOUCE_EXTENSION_PUBLIC_KEY = "PublicConfig"
    RESOUCE_EXTENSION_PUBLIC_TYPE = "Public"

    class DISABLE_NLA_EXTENSION_REFRENCE:
        REFRENCE_NAME = "CustomScriptExtension"
        EXTENSION_NAME = "CustomScriptExtension"
        PUBLISHER = "Microsoft.Compute"
        VERSION = "1.*"
        FILE_URIS = ["https://opentech0storage.blob.core.chinacloudapi.cn/public-scripts/disablenla.ps1"]
        RUN = "powershell -ExecutionPolicy Unrestricted -file disablenla.ps1"

        CONFIG_KEY_FILE_URIS = "fileUris"
        CONFIG_KEY_RUN = "commandToExecute"
