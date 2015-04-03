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
__author__ = 'Yifu Huang'

from src.azureformation.azureoperation.utility import (
    load_template_from_experiment,
    set_template_virtual_environment_count,
)
from src.azureformation.azureoperation.templateUnit import (
    TemplateUnit,
)


class TemplateFramework():
    VIRTUAL_ENVIRONMENTS = 'virtual_environments'

    def __init__(self, experiment_id):
        self.template = load_template_from_experiment(experiment_id)
        set_template_virtual_environment_count(experiment_id, len(self.template[self.VIRTUAL_ENVIRONMENTS]))

    def get_template_units(self):
        return map(TemplateUnit, self.template[self.VIRTUAL_ENVIRONMENTS])
