# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

"""constants used in template files"""


class __Template(object):
    """constants in template level"""
    TEMPLATE_NAME = 'name'
    DESCRIPTION = 'description'
    # todo delete VIRTUAL_ENVIRONMENTS
    VIRTUAL_ENVIRONMENTS = 'virtual_environments'
    VIRTUAL_ENVIRONMENT = 'virtual_environment'
    VIRTUAL_ENVIRONMENT_PROVIDER = "provider"


class __DockerTemplate(__Template):
    IMAGE = "image"
    NET_NAME = "name"
    NET_PROTOCOL = "protocol"
    NET_PORT = "port"


class __DockerUnit(object):
    IMAGE = "image"
    NET_CONFIG = "network"
    NET_NAME = "name"
    NET_PROTOCOL = "protocol"
    NET_PORT = "port"


class __K8sTemplate(__Template):
    YAML_TEMPLATE = "yaml_template"


class __K8sUnit(object):
    YAML_TEMPLATE = "yaml_template"


TEMPLATE = __Template()
DOCKER_TEMPLATE = __DockerTemplate()
DOCKER_UNIT = __DockerUnit()
K8S_TEMPLATE = __K8sTemplate()
K8S_UNIT = __K8sUnit()
