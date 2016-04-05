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

import random
import string
import pexpect
from os.path import abspath, dirname, realpath

from hackathon.hmongo.models import Experiment, VirtualEnvironment
from hackathon.constants import VE_PROVIDER, VEStatus, VERemoteProvider, EStatus
from expr_starter import ExprStarter


class DockerExprStarter(ExprStarter):
    def _internal_rollback(self, context):
        # currently rollback share the same process as stop
        self._internal_stop_expr(context)

    def _stop_virtual_environment(self, virtual_environment, experiment, context):
        pass

    def _internal_start_expr(self, context):
        for unit in context.template_content.units:
            try:
                self.__start_virtual_environment(context, unit)
            except Exception as e:
                self.log.error(e)
                self._on_virtual_environment_failed(context)

    def _internal_start_virtual_environment(self, context):
        raise NotImplementedError()

    def _get_docker_proxy(self):
        raise NotImplementedError()

    def _internal_stop_expr(self, context):
        expr = Experiment.objects(id=context.experiment_id).first()
        if not expr:
            return

        if len(expr.virtual_environments) == 0:
            expr.status = EStatus.ROLL_BACKED
            expr.save()
            return

        # delete containers and change expr status
        for ve in expr.virtual_environments:
            context = context.copy()  # create new context for every virtual_environment
            context.virtual_environment_name = ve.name
            self._stop_virtual_environment(ve, expr, context)

    def __start_virtual_environment(self, context, docker_template_unit):
        origin_name = docker_template_unit.get_name()
        prefix = str(context.experiment_id)[0:9]
        suffix = "".join(random.sample(string.ascii_letters + string.digits, 8))
        new_name = '%s-%s-%s' % (prefix, origin_name, suffix.lower())
        docker_template_unit.set_name(new_name)
        self.log.debug("starting to start container: %s" % new_name)

        # db document for VirtualEnvironment
        ve = VirtualEnvironment(provider=VE_PROVIDER.DOCKER,
                                name=new_name,
                                image=docker_template_unit.get_image_with_tag(),
                                status=VEStatus.INIT,
                                remote_provider=VERemoteProvider.Guacamole)
        # create a new context for current ve only
        context = context.copy()
        experiment = Experiment.objects(id=context.experiment_id).no_dereference().only("virtual_environments").first()
        experiment.virtual_environments.append(ve)
        experiment.save()

        # start container remotely , use hosted docker or alauda docker
        context.virtual_environment_name = ve.name
        context.unit = docker_template_unit
        self._internal_start_virtual_environment(context)

    def _enable_guacd_file_transfer(self, context):
        """
        This function should be invoked after container is started in alauda_docker.py and hosted_docker.py
        :param ve: virtual environment
        """
        expr = Experiment.objects(id=context.experiment_id).no_dereference().first()
        virtual_env = expr.virtual_environments.get(name=context.virtual_environment_name)
        remote = virtual_env.remote_paras

        p = pexpect.spawn("scp -P %s %s %s@%s:/usr/local/sbin/guacctl" %
                          (remote["port"],
                           abspath("%s/../expr/guacctl" % dirname(realpath(__file__))),
                           remote["username"],
                           remote["hostname"]))
        i = p.expect([pexpect.TIMEOUT, 'yes/no', 'password: '])
        if i == 1:
            p.sendline("yes")
            i = p.expect([pexpect.TIMEOUT, 'password:'])

        if i != 0:
            p.sendline(remote["password"])
            p.expect(pexpect.EOF)
        p.close()
