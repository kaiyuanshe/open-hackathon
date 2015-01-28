import sys

sys.path.append("..")

from flask import Flask,request,g
from hackathon.log import log
import json

class GuacamoleInfo():

    def getConnectInfo(self):

        connection_name = request.args.get("id")
        userID = g.user.get_user_id()
        guacadconfig = g.user.virtual_environments.filter_by(remote_provider='guacamole',name=connection_name,user_id=userID,status=1).first()

        debuginfo = guacadconfig.remote_paras
        log.info(debuginfo)
        return guacadconfig.remote_paras