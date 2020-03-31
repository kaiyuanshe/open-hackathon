# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import yaml
from collections import defaultdict

from hackathon.constants import VE_PROVIDER
from hackathon.template.template_constants import TEMPLATE, DOCKER_TEMPLATE
from hackathon.template.docker_template_unit import DockerTemplateUnit
from hackathon.template.k8s_template_unit import K8STemplateUnit

__all__ = ["TemplateContent"]


class NetworkConfig:

    def __init__(self, name, protocol, port):
        self.name = name
        self.protocol = protocol
        self.port = port


class TemplateContent:
    """The content of a template in dict format

    It's the only type that for template saving and loading.
    """

    def __init__(self, name, description, environment):
        self.name = name
        self.description = description
        self.environment = environment

        self.provider = None

        self.docker_image = None
        self.network_configs = []

        self.yml_template = ""
        self.template_args = {}

        # FIXME unit bundle is useless for K8s
        self.resource = defaultdict(list)
        self.cluster_info = None
        self.units = []

    def from_docker_image(self, docker_image, network_configs):
        self.provider = VE_PROVIDER.DOCKER
        self.docker_image = docker_image

        for cfg in network_configs:
            self.network_configs.append(NetworkConfig(
                cfg[DOCKER_TEMPLATE.NET_NAME],
                cfg[DOCKER_TEMPLATE.NET_PROTOCOL],
                cfg[DOCKER_TEMPLATE.NET_PORT],
            ))

    def from_kube_yaml_template(self, yml_template, template_args):
        self.provider = VE_PROVIDER.K8S
        self.yml_template = yml_template
        self.template_args = template_args

    def is_valid(self):
        if self.provider is None:
            return False

        if self.provider == VE_PROVIDER.DOCKER:
            return True

        if self.provider == VE_PROVIDER.K8S:
            # todo Make sure yml content is different in different environments
            pass

    def get_resource(self, resource_type):
        # always return a list of resource desc dict or empty
        return self.resource[resource_type]

    @classmethod
    def load_from_template(cls, template):
        tc = TemplateContent(template.name, template.description, TemplateContent.load_environment(t))
        if template.provider == VE_PROVIDER.K8S:
            tc.from_kube_yaml_template(template.content, template.template_args)
        elif template.provider == VE_PROVIDER.DOCKER:
            tc.from_docker_image(
                template.docker_image,
                [cfg.to_dic() for cfg in template.network_configs],
            )
        else:
            raise RuntimeError("Using deprecated VirtualEnvironment provider")
        return tc

    @classmethod
    def load_environment(cls, environment_config):
        provider = int(environment_config[TEMPLATE.VIRTUAL_ENVIRONMENT_PROVIDER])
        if provider == VE_PROVIDER.DOCKER:
            return DockerTemplateUnit(environment_config)
        elif provider == VE_PROVIDER.K8S:
            return K8STemplateUnit(environment_config)
        else:
            raise Exception("unsupported virtual environment provider")

    # FIXME deprecated this when support K8s ONLY
    def to_dict(self):
        dic = {
            TEMPLATE.TEMPLATE_NAME: self.name,
            TEMPLATE.DESCRIPTION: self.description
        }

        def convert_to_dict(unit):
            if unit.provider == VE_PROVIDER.DOCKER:
                return unit.dic
            elif unit.provider == VE_PROVIDER.AZURE:
                raise NotImplementedError()
            return unit

        dic[TEMPLATE.VIRTUAL_ENVIRONMENTS] = list(map(convert_to_dict, self.units))
        return dic
