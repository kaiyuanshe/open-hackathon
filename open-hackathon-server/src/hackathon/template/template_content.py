# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys
import yaml
from collections import defaultdict

sys.path.append("..")

from hackathon.constants import VE_PROVIDER
from template_constants import TEMPLATE
from docker_template_unit import DockerTemplateUnit
from azure_template_unit import AzureTemplateUnit
from k8s_template_unit import K8STemplateUnit

__all__ = ["TemplateContent"]


class TemplateContent:
    """The content of a template in dict format

    It's the only type that for template saving and loading.
    """

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.resource = defaultdict(list)

        self.cluster_info = None

        # FIXME unit bundle is useless for K8s
        self.units = []

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
                return AzureTemplateUnit(unit_dict)
            elif provider == VE_PROVIDER.K8S:
                return K8STemplateUnit(unit_dict)
            else:
                raise Exception("unsupported virtual environment provider")

        units = map(convert_to_unit, args[TEMPLATE.VIRTUAL_ENVIRONMENTS])
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
                return unit.virtual_environment
            return unit

        dic[TEMPLATE.VIRTUAL_ENVIRONMENTS] = map(convert_to_dict, self.units)
        return dic
