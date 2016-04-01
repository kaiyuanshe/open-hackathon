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

from expr_starter import ExprStarter
from hackathon import RequiredFeature
from hackathon.hmongo.models import VirtualEnvironment
from hackathon.constants import VE_PROVIDER, VERemoteProvider, VEStatus
from hackathon.hackathon_response import internal_server_error


class AzureVMExprStarter(ExprStarter):
    azure_cert_manager = RequiredFeature("azure_cert_manager")
    azure_formation = RequiredFeature("azure_formation")

    def _internal_start_expr(self, context):
        try:
            # TODO: context.hackathon may be None when tesing a template before any hackathon bind it
            azure_keys = context.hackathon.azure_keys
            # TODO: which key to use?
            azure_key = azure_keys[0]

            # create virtual environments for units
            expr_id = context.experiment.id
            ves = []
            for unit in context.template_content.units:
                ve = VirtualEnvironment(
                    provider=VE_PROVIDER.AZURE,
                    # TODO: when to set name?
                    name=self.azure_formation.get_virtual_machine_name(unit.get_virtual_machine_name(),
                                                                       expr_id),
                    image=unit.get_image_name(),
                    status=VEStatus.INIT,
                    remote_provider=VERemoteProvider.Guacamole,
                    experiment=context.experiment)
                self.db.add_object(ve)
                ves.append(ve)

            # TODO: elimate virtual_environments arg
            self.azure_formation.start_vm(expr_id, azure_key, context.template_content.units, ves)
        except Exception as e:
            self.log.error(e)
            return internal_server_error('Failed starting azure vm')

    def _internal_stop_expr(self, context):
        try:
            # todo support delete azure vm
            # hosted_docker = RequiredFeature("hosted_docker")
            # af = AzureFormation(hosted_docker.load_azure_key_id(expr_id))
            # af.stop(expr_id, AVMStatus.STOPPED_DEALLOCATED)
            expr = context.experiment
            template = expr.template
            template_content = self.template_library.load_template(template)
            # TODO: save azure key in experiment
            azure_key = context.experiment.azure_key

            # TODO: elimate virtual_environments arg and expr_id arg
            self.azure_formation.stop_vm(
                expr.id, azure_key, template_content.units, expr.virtual_environments.all(), expr.id)
        except Exception as e:
            self.log.error(e)
            return internal_server_error('Failed stopping azure')
