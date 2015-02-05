import sys

sys.path.append("..")

from flask import request, g
from hackathon.enum import VirtualEnvStatus, RemoteProvider
from hackathon.azureautodeploy.azureUtil import *
import json


class GuacamoleInfo():
    def getConnectInfo(self):
        connection_name = request.args.get("id")
        guacadconfig = g.user.virtual_environments.filter_by(remote_provider=RemoteProvider.Guacamole,
                                                             name=connection_name,
                                                             user_id=g.user.id,
                                                             status=VirtualEnvStatus.Running).first()
        # azure vm
        if guacadconfig is None:
            user_template = db_adapter.find_first_object(UserTemplate, user=g.user)
            vm = db_adapter.find_first_object(UserResource,
                                              type=VIRTUAL_MACHINE,
                                              name=connection_name,
                                              status=RUNNING,
                                              user_template=user_template)
            guacadconfig = db_adapter.find_first_object(VMConfig,
                                                        remote_provider=RemoteProvider.Guacamole,
                                                        virtual_machine_id=vm.id)
        log.debug("get guacamole config by id: %s, paras: %s" % (connection_name, guacadconfig.remote_paras))
        return json.loads(guacadconfig.remote_paras)