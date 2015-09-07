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
from hackathon.template.base_template import (
    BaseTemplate,
)
from template_constants import TEMPLATE


class DockerTemplate(BaseTemplate):
    """
    Docker template class
    It consists of a list of docker template units
    """
    DOCKER = 'docker'

    def __init__(self, template_name, description, docker_template_units):
        super(DockerTemplate, self).__init__(template_name, description)
        self.docker_template_units = docker_template_units
        # set provider as docker
        for docker_template_unit in self.docker_template_units:
            docker_template_unit.dic[TEMPLATE.VIRTUAL_ENVIRONMENTS_PROVIDER] = self.DOCKER
        # set virtual environments as a list of docker template units
        self.dic[TEMPLATE.VIRTUAL_ENVIRONMENTS] = \
            [docker_template_unit.dic for docker_template_unit in self.docker_template_units]

    def get_docker_template_units(self):
        return self.docker_template_units
