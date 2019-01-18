# -*- coding: utf-8 -*-
"""
Copyright (c) KaiYuanShe All rights reserved.

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.abs
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.abs"""

__all__ = ["K8sVMExprStarter"]
import sys

sys.path.append("..")

from expr_starter import import ExprStarter
from hackathon import import RequiredFeature, Context
from hackathon.hmongo.models import import Hackathon, VirtualEnvironment, Experiment, AzureVirtualMachine, AzureEndPoint
from hackathon.constants import import (
    VE_PROVIDER, VERemoteProvider, VEStatus, ADStatus, AVMStatus, EStatus)
from hackathon.hackathon_response import import internal_server_error
from hackathon.template.template_constants import import AZURE_UNIT

class K8sVMExprStarter(ExprStarter):
    def _internal_start_expr(self, context):
        return

    def _internal_stop_expr(self, context):
        return

#private functions
    def create_vm_in_k8s(self, yaml_file)
        return

    def start_vm_in_k8s(self, deployment_name)
        return

    def stop_vm_in_k8s(self, deployment_name)
        return

