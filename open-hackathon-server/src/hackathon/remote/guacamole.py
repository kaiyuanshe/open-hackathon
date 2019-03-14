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
