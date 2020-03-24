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

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.resource = defaultdict(list)

        self.provider = None

        self.docker_image = None
        self.network_configs = []

        self.yml_template = ""
        self.template_args = {}

        # FIXME unit bundle is useless for K8s
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

    def expr_k8s_yaml(self, expr_name) -> str:
        # todo Generate usable expr k8s yaml content
        pass

    @classmethod
    def from_yaml(cls, template_model, yaml_content):
        yamls = yaml.load_all(yaml_content)
        resource = defaultdict(list)

        for y in yamls:
            kind = str(y['kind']).lower()
            resource[kind].append(y)

        tc = TemplateContent(template_model.name, template_model.description)
        tc.resource = resource

        return tc

    def get_resource(self, resource_type):
        # always return a list of resource desc dict or empty
        return self.resource[resource_type]

    # FIXME deprecated this when support K8s ONLY
    @staticmethod
    def from_dict(args):
        name = args[TEMPLATE.TEMPLATE_NAME]
        description = args[TEMPLATE.DESCRIPTION]

        def convert_to_unit(unit_dict):
            provider = int(unit_dict[TEMPLATE.VIRTUAL_ENVIRONMENT_PROVIDER])
            if provider == VE_PROVIDER.DOCKER:
                return DockerTemplateUnit(unit_dict)
            elif provider == VE_PROVIDER.AZURE:
                raise NotImplementedError()
            elif provider == VE_PROVIDER.K8S:
                return K8STemplateUnit(unit_dict)
            else:
                raise Exception("unsupported virtual environment provider")

        units = list(map(convert_to_unit, args[TEMPLATE.VIRTUAL_ENVIRONMENTS]))
        tc = TemplateContent(name, description)
        tc.units = units
        return tc

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
