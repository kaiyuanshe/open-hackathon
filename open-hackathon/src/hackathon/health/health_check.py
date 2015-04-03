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
from hackathon.constants import HEALTH_STATE
from hackathon.docker import *
from hackathon.azureautodeploy.azureImpl import *
from hackathon.functions import *
from sqlalchemy import __version__

STATUS = "status"
DESCRIPTION = "description"
VERSION = "version"


class HealthCheck():
    def reportHealth(self):
        pass


class MySQLHealthCheck(HealthCheck):
    def __init__(self):
        self.db = db_adapter

    def reportHealth(self):
        try:
            self.db.count(User)
            return {
                STATUS: HEALTH_STATE.OK,
                VERSION: __version__
            }
        except Exception as e:
            return {
                STATUS: HEALTH_STATE.ERROR,
                VERSION: __version__,
                DESCRIPTION: e.message
            }


class DockerHealthCheck(HealthCheck):
    def __init__(self):
        self.db = db_adapter
        self.docker = OssDocker()

    def reportHealth(self):
        try:
            hosts = self.db.find_all_objects(DockerHostServer)
            alive = 0
            for host in hosts:
                if self.docker.ping(host):
                    alive += 1
            if alive == len(hosts):
                return {
                    STATUS: HEALTH_STATE.OK
                }
            elif alive > 0:
                return {
                    STATUS: HEALTH_STATE.WARNING,
                    DESCRIPTION: 'at least one docker host servers are down'
                }
            else:
                return {
                    STATUS: HEALTH_STATE.ERROR,
                    DESCRIPTION: 'all docker host servers are down'
                }
        except Exception as e:
            return {
                STATUS: HEALTH_STATE.ERROR,
                "description": e.message
            }


class GuacamoleHealthCheck(HealthCheck):
    # todo now check only server status
    def __init__(self):
        self.guacamole_url = get_config("guacamole.host") + '/guacamole'

    def reportHealth(self):
        try:
            req = requests.get(self.guacamole_url)
            log.debug(req.status_code)
            if req.status_code == 200:
                return {
                    STATUS: HEALTH_STATE.OK
                }
        except Exception as e:
            log.error(e)
        return {
            STATUS: HEALTH_STATE.ERROR
        }


class AzureHealthCheck(HealthCheck):
    def __init__(self):
        self.azure = AzureImpl()
        sub_id = get_config("azure.subscriptionId")
        cert_path = get_config('azure.certPath')
        service_host_base = get_config("azure.managementServiceHostBase")
        self.azure.connect(sub_id, cert_path, service_host_base)

    def reportHealth(self):
        if self.azure.ping():
            return {
                STATUS: HEALTH_STATE.OK
            }
        else:
            return {
                STATUS: HEALTH_STATE.ERROR
            }


g = GuacamoleHealthCheck()
print g.reportHealth()