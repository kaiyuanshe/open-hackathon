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
