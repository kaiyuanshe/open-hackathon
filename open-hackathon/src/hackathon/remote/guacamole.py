from flask import Flask,request,g
from flask_login import current_user
from hackathon.log import log
from hackathon import app
from hackathon.database.models import User
import json



@app.before_request
def before_request():
    g.user = current_user
    # session.permanent = True


@app.route('/getguacadconfig')
def getguacadconfig():

	log.info("call getguacadconfig")
	connection_name = request.args.get("id")
	log.info("connection name is " + connection_name)

	userID = g.user.get_user_id()

	guacdconfig = g.user.virtual_environments.filter_by(remote_provider='guacamole',name=connection_name,user_id=userID,status=1).all()
	log.info('guacamole jsonString is :' + json.dumps(guacdconfig))

	return guacdconfig