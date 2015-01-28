import sys

sys.path.append("..")

from flask import request, g
from hackathon.log import log
from hackathon.enum import VirtualEnvStatus, RemoteProvider
import json


class GuacamoleInfo():
    def getConnectInfo(self):
        connection_name = request.args.get("id")
        guacadconfig = g.user.virtual_environments.filter_by(remote_provider=RemoteProvider.Guacamole,
                                                             name=connection_name,
                                                             user_id=g.user.id,
                                                             status=VirtualEnvStatus.Running).first()

        log.debug("get guacamole config by id: %s, paras: %s" % (connection_name, guacadconfig.remote_paras))
        return json.loads(guacadconfig.remote_paras)