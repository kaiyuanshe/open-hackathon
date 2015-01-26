from flask import Flask,request,g
from flask_restful import Resource
from hackathon.decorators import token_required
from hackathon.log import log
import json

class guacamoleResource(Resource):

	@token_required
	def get(self):

		log.info("call getguacadconfig")
		connection_name = request.args.get("id")
		log.info("connection name is " + connection_name)

		userID = g.user.get_user_id()
		guacadconfig = g.user.virtual_environments.filter_by(remote_provider='guacamole',name=connection_name,user_id=userID,status=1).first()

		debuginfo = guacadconfig.remote_paras

		log.info("guacamole configuration is :" + guacadconfig.remote_paras)

		return guacadconfig.remote_paras