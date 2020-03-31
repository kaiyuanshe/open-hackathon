# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

"""constants used in template files"""


class TEMPLATE:
    """constants in template level"""
    TEMPLATE_NAME = 'name'
    DESCRIPTION = 'description'
    # todo delete VIRTUAL_ENVIRONMENTS
    VIRTUAL_ENVIRONMENTS = 'virtual_environments'
    VIRTUAL_ENVIRONMENT = 'virtual_environment'
    VIRTUAL_ENVIRONMENT_PROVIDER = "provider"


class DOCKER_TEMPLATE:
    IMAGE = "image"
    NET_NAME = "name"
    NET_PROTOCOL = "protocol"
    NET_PORT = "port"


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


class K8S_UNIT:
    """constants for k8s virtual_environment in template file"""
    NAME = 'name'

    CONFIG_CLUSTER = 'cluster'
    CONFIG_NAMESPACES = "namespace"
    CONFIG_API_SERVER = "api_url"  # K8s ApiServer url
    CONFIG_API_TOKEN = "token"  # K8s namespaced ServiceAccount Token

    PORTS = 'ports'
    PORTS_NAME = 'name'
    PORTS_PORT = 'port'
    PORTS_PROTOCOL = 'protocol'
    PORTS_PUBLIC = "public"
    PORTS_PUBLIC_PORT = 'public_port'

    REMOTE = 'remote'
    REMOTE_PROVIDER = 'provider'
    REMOTE_PROTOCOL = 'protocol'
    REMOTE_USERNAME = 'username'
    REMOTE_PASSWORD = 'password'
    REMOTE_PORT = 'port'

    # remote parameter name
    REMOTE_PARAMETER_NAME = 'name'
    REMOTE_PARAMETER_DISPLAY_NAME = 'displayname'
    REMOTE_PARAMETER_HOST_NAME = 'hostname'
    REMOTE_PARAMETER_PROTOCOL = 'protocol'
    REMOTE_PARAMETER_PORT = 'port'
    REMOTE_PARAMETER_USER_NAME = 'username'
    REMOTE_PARAMETER_PASSWORD = 'password'

    IMAGES = 'images'
    IMAGES_IMAGE = 'image'

    RESOURCES = 'resource'
    RESOURCES_REQUESTS = 'requests'
    RESOURCES_REQUESTS_CPU = 'cpu'
    RESOURCES_REQUESTS_MEM = 'mem'
    RESOURCES_LIMITS = 'limits'
    RESOURCES_LIMITS_CPU = 'cpu'
    RESOURCES_LIMITS_MEM = 'mem'
