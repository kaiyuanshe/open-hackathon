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

__all__ = ["K8SExprStarter"]
import sys

sys.path.append("..")

from expr_starter import import ExprStarter
from hackathon import import RequiredFeature, Context
from hackathon.hmongo.models import import Hackathon, VirtualEnvironment, Experiment, AzureVirtualMachine, AzureEndPoint
from hackathon.constants import import (
    VE_PROVIDER, VERemoteProvider, VEStatus, ADStatus, AVMStatus, EStatus)
from hackathon.hackathon_response import import internal_server_error
from hackathon.template.template_constants import import AZURE_UNIT

class K8SExprStarter(ExprStarter):

	def start_expr(self, context):
        """To start a new Experiment asynchronously

        :type context: Context
        :param context: the execution context.

        """
        expr = Experiment(status=EStatus.INIT,
                          template=context.template,
                          user=context.user,
                          virtual_environments=[],
                          hackathon=context.hackathon)
        expr.save()

        template_content = self.template_library.load_template(context.template)
        expr.status = EStatus.STARTING
        expr.save()

        # context contains complex object, we need create another serializable one with only simple fields
        new_context = Context(template_content=template_content,
                              template_name=context.template.name,
                              hackathon_id=context.hackathon.id,
                              experiment_id=expr.id)
        if context.get("user", None):
            new_context.user_id = context.user.id
        self._internal_start_expr(new_context)
        new_context.experiment = expr
        return new_context

    def stop_expr(self, context):
        """Stop experiment asynchronously

        :type context: Context
        :param context: the execution context.

        """
        return self._internal_stop_expr(context)

    def rollback(self, context):
        """cancel/rollback a expr which is in error state

        :type context: Context
        :param context: the execution context.

        """
        return self._internal_rollback(context)

    def _internal_start_expr(self, context):
        # set up virtual environment
        #experiment.virtual_environments.append(VirtualEnvironment(
        #    provider=VE_PROVIDER.K8S,
        #    name=vm_name,
        #    image=unit.get_image_name(),
        #    status=VEStatus.INIT,
        #    remote_provider=VERemoteProvider.Guacamole))
        raise NotImplementedError()

    def _internal_stop_expr(self, context):
        raise NotImplementedError()

    def _internal_rollback(self, context):
        raise NotImplementedError()

#private functions
    def create_vm_in_k8s(self, yaml_file)
        return

    def start_vm_in_k8s(self, deployment_name)
        return

    def stop_vm_in_k8s(self, deployment_name)
        return

