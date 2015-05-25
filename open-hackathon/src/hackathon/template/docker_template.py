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


class DockerTemplate(BaseTemplate):
    """
    Docker template class
    It consists of a list of docker template units
    """
    DOCKER = 'docker'

    def __init__(self, expr_name, docker_template_units):
        super(DockerTemplate, self).__init__(expr_name)
        # set provider as docker
        for docker_template_unit in docker_template_units:
            docker_template_unit.dic[self.VIRTUAL_ENVIRONMENTS_PROVIDER] = self.DOCKER
        # set virtual environments as a list of docker template units
        self.dic[self.VIRTUAL_ENVIRONMENTS] = [docker_template_unit.dic for docker_template_unit in docker_template_units]