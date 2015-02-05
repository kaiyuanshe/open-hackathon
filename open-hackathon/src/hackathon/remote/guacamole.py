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
        connection_name = request.args.get("id")
        guacadconfig = g.user.virtual_environments.filter_by(remote_provider=RemoteProvider.Guacamole,
                                                             name=connection_name,
                                                             user_id=g.user.id,
                                                             status=VirtualEnvStatus.Running).first()
        # azure vm
        if guacadconfig is None:
            guacadconfig = db_adapter.find_first_object(VMConfig, virtual_machine_id=connection_name)
        log.debug("get guacamole config by id: %s, paras: %s" % (connection_name, guacadconfig.remote_paras))
        return json.loads(guacadconfig.remote_paras)