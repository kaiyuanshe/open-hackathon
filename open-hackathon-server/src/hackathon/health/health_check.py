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

from hackathon.hazure.cloud_service_adapter import CloudServiceAdapter
from hackathon.hmongo.models import AzureKey, User

sys.path.append("..")
import requests
import abc

from hackathon.constants import HEALTH_STATUS
from hackathon import RequiredFeature, Component

__all__ = [
    "HostedDockerHealthCheck",
    "AlaudaDockerHealthCheck",
    "GuacamoleHealthCheck",
    "StorageHealthCheck"
]

STATUS = "status"
DESCRIPTION = "description"
VERSION = "version"


class HealthCheck(Component):
    """Base class for health check item"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def report_health(self):
        pass


class MongoDBHealthCheck(HealthCheck):
    """Check the health status of MongoDB."""

    def report_health(self):
        """ Report the status by querying mongodb server info

        Will return OK if server info returned
       """
        try:
            server_info = self.db.client.server_info()
            server_info[STATUS] = HEALTH_STATUS.OK
            return server_info
        except Exception as e:
            return {
                STATUS: HEALTH_STATUS.ERROR,
                DESCRIPTION: e.message
            }


class HostedDockerHealthCheck(HealthCheck):
    """Report status of hostdd docker

    see more on docker/hosted_docker.py
    """

    def __init__(self):
        self.hosted_docker = RequiredFeature("hosted_docker_proxy")

    def report_health(self):
        return self.hosted_docker.report_health()


class AlaudaDockerHealthCheck(HealthCheck):
    """Report status of Alauda service

    see more on docker/alauda_docker.py
    """

    def __init__(self):
        self.alauda_docker = RequiredFeature("alauda_docker_proxy")

    def report_health(self):
        return self.alauda_docker.report_health()


class GuacamoleHealthCheck(HealthCheck):
    """Check the status of Guacamole Server by request its homepage"""

    def __init__(self):
        self.guacamole_url = self.util.get_config("guacamole.host") + '/guacamole'

    def report_health(self):
        try:
            req = requests.get(self.guacamole_url)
            self.log.debug(req.status_code)
            if req.status_code == 200:
                return {
                    STATUS: HEALTH_STATUS.OK
                }
        except Exception as e:
            self.log.error(e)
        return {
            STATUS: HEALTH_STATUS.ERROR
        }


class AzureHealthCheck(HealthCheck):
    """Check the status of azure to make sure config is right and azure is available"""

    def report_health(self):
        azure_key = AzureKey.objects().first()
        if not azure_key:
            return {
                STATUS: HEALTH_STATUS.WARNING,
                DESCRIPTION: "No Azure key found"
            }
        service = CloudServiceAdapter(azure_key.id)
        if service.ping():
            return {
                STATUS: HEALTH_STATUS.OK,
                "type": "Azure Storage"
            }
        else:
            return {
                STATUS: HEALTH_STATUS.ERROR
            }


class StorageHealthCheck(HealthCheck):
    """Check the status of storage"""

    def report_health(self):
        self.storage.report_health()

    def __init__(self):
        self.storage = RequiredFeature("storage")
