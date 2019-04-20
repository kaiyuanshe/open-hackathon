# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")
from flask import request, g

from hackathon.constants import VEStatus, VERemoteProvider
from hackathon.hmongo.models import Experiment
from hackathon.hackathon_response import forbidden, not_found
from hackathon import Component
from hackathon.template.template_constants import K8S_UNIT
import random


class GuacamoleInfo(Component):
    def getConnectInfo(self):
        connection_name = request.args.get("name")
        expr = Experiment.objects(virtual_environments__name=connection_name).no_dereference().first()
        if not expr:
            return not_found("not_found")

        if expr.user.id != g.user.id:
            return forbidden("forbidden")

        remote_paras = expr.virtual_environments.get(name=connection_name).remote_paras
        # TODO Support DYNAMIC host/port in case of they cannot be determined on provision phase
        if K8S_UNIT.REMOTE_PARAMETER_HOST_NAME not in remote_paras:
            # TTT
            available_public_ips = self.unit.safe_get_config("ukylin.k8s.ips",
                                                             ["119.3.202.71",
                                                              "49.4.90.39"
                                                              ])
            random_ip = available_public_ips[random.randint(0, len(available_public_ips) - 1)]
            remote_paras[K8S_UNIT.REMOTE_PARAMETER_HOST_NAME] = random_ip

        self.log.debug("get guacamole config by id: %s, paras: %r" % (connection_name, remote_paras))
        return remote_paras
        # return {
        # "displayname": "ubuntu", "hostname": "139.217.133.53",
        # "name": "174-ubuntu", "password": "acowoman",
        # "port": 10026, "protocol": "ssh", "username": "root"
        # }
