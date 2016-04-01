# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

import sys

sys.path.append("..")
from flask import request, g

from hackathon.constants import VEStatus, VERemoteProvider
from hackathon.hmongo.models import Experiment
from hackathon.hackathon_response import forbidden, not_found
from hackathon import Component


class GuacamoleInfo(Component):
    def getConnectInfo(self):
        connection_name = request.args.get("name")
        expr = Experiment.objects(virtual_environments__name=connection_name).no_dereference().first()
        if not expr:
            return not_found("not_found")

        if expr.user.id != g.user.id:
            return forbidden("forbidden")

        ve = expr.virtual_environments.get(name=connection_name)
        self.log.debug("get guacamole config by id: %s, paras: %r" % (connection_name, ve.remote_paras))
        return ve.remote_paras
        # return {
        # "displayname": "ubuntu", "hostname": "139.217.133.53",
        # "name": "174-ubuntu", "password": "acowoman",
        # "port": 10026, "protocol": "ssh", "username": "root"
        # }
