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
from flask import (
    request,
    g,
)
from hackathon.enum import (
    VEStatus,
    VERemoteProvider,
    EStatus,
)
from hackathon.log import (
    log,
)
from hackathon.database import (
    db_adapter,
)
from hackathon.database.models import (
    VirtualEnvironment,
    Experiment,
)
import json


class GuacamoleInfo():
    def getConnectInfo(self):
        connection_name = request.args.get("id")
        experiment = db_adapter.find_first_object_by(Experiment,
                                                     status=EStatus.Running,
                                                     user=g.user)
        guacamole_config = db_adapter.find_first_object_by(VirtualEnvironment,
                                                           name=connection_name,
                                                           status=VEStatus.Running,
                                                           remote_provider=VERemoteProvider.Guacamole,
                                                           experiment=experiment)
        log.debug("get guacamole config by id: %s, paras: %s" % (connection_name, guacamole_config.remote_paras))
        return json.loads(guacamole_config.remote_paras)