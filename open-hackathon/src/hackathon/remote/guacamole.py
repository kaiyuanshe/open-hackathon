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
from hackathon.enum import VirtualEnvStatus, RemoteProvider
from hackathon.azureautodeploy.azureUtil import *
import json
from hackathon.database import *
from hackathon.database.models import *


class GuacamoleInfo():
    def getConnectInfo(self):
        connection_name = request.args.get("name")
        guacadconfig = g.user.virtual_environments.filter_by(remote_provider=RemoteProvider.Guacamole,
                                                             name=connection_name,
                                                             user_id=g.user.id,
                                                             status=VirtualEnvStatus.Running).first()
        # azure vm
        if guacadconfig is None:
            vm = db_adapter.find_first_object_by(UserResource,
                                                 type=VIRTUAL_MACHINE,
                                                 name=connection_name,
                                                 status=RUNNING)
            guacadconfig = db_adapter.find_first_object_by(VMConfig,
                                                           remote_provider=RemoteProvider.Guacamole,
                                                           virtual_machine_id=vm.id)
        log.debug("get guacamole config by id: %s, paras: %s" % (connection_name, guacadconfig.remote_paras))
        return json.loads(guacadconfig.remote_paras)