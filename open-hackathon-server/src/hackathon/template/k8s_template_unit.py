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

from hackathon.template.template_constants import K8S_UNIT
from hackathon.template.template_unit import TemplateUnit
from hackathon.constants import VE_PROVIDER

__all__ = ["K8STemplateUnit"]


class K8STemplateUnit(TemplateUnit):
    """
    Smallest unit in k8s template
    """

    def __init__(self, config):
        super(K8STemplateUnit, self).__init__(VE_PROVIDER.K8S)

        self.yml_template = config[K8S_UNIT.YAML_TEMPLATE]
        self.template_args = {}

    def gen_k8s_yaml(self, expr_name):
        pass

    def is_valid(self):
        # todo Make sure yml content is different in different environments
        pass
