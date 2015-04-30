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

import sys
sys.path.append("..")
from hackathon.azureformation.templateFramework import (
    TemplateFramework,
)
from hackathon.azureformation.utility import (
    MDL_CLS_FUNC,
    run_job,
)


class AzureFormation:
    """
    Azure cloud service management
    For logic: besides resources created by this program itself, it can reuse other storage,
    container, cloud service and deployment exist in azure (by sync them into database)
    For template: a template consists of a list of virtual environments, and a virtual environment
    is a virtual machine with its storage account, container, cloud service and deployment
    Notice: It requires exclusive access when Azure performs an async operation on a deployment
    """

    def __init__(self, azure_key_id):
        self.azure_key_id = azure_key_id

    def create(self, experiment_id):
        template_framework = TemplateFramework(experiment_id)
        for template_unit in template_framework.get_template_units():
            # create storage account
            run_job(MDL_CLS_FUNC[0],
                    (self.azure_key_id, ),
                    (experiment_id, template_unit))

    def stop(self, experiment_id, need_status):
        template_framework = TemplateFramework(experiment_id)
        for template_unit in template_framework.get_template_units():
            # stop virtual machine
            run_job(MDL_CLS_FUNC[17],
                    (self.azure_key_id, ),
                    (experiment_id, template_unit, need_status))