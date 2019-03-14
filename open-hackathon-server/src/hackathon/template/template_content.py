# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

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

    def __init__(self, name, description, units):
        self.name = name
        self.description = description
        self.units = units

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
        return TemplateContent(name, description, units)

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
