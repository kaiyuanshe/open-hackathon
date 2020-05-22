# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")
import requests
import json

from flask import session, request
from flask_login import logout_user

from client.functions import get_config
from client.log import log
from client.md5 import encode
from client.constants import LOGIN_PROVIDER
from client.user.user import User


class LoginManagerHelper():
    '''Helper class for flask-login.LoginManager'''
    headers = {"Content-Type": "application/json"}
    login_url = get_config("endpoint.hackathon_api") + "/api/user/login"
    authing_url = get_config("endpoint.hackathon_api") + "/api/user/authing"

    def load_user(self, id):
        try:
            req = requests.get(self.login_url, {"id": id})
            login_user = User(json.loads(req.content))
            return login_user
        except Exception as e:
            log.error(e)
            return None

    def logout(self, token):


        session.pop("token", "")
        logout_user()

    def login(self, provider):
        if provider == LOGIN_PROVIDER.DB:
            return self.__mysql_login()
        else:
            return self.__oauth_login(provider)

    def authing(self, user_info):
        try:
            req = requests.post(self.authing_url, json=user_info, headers=self.headers)
            resp = req.json()
            if resp:
                # if login isn't successful, it will return None
                login_user = User(resp["user"])
                log.debug("Login successfully %s" % login_user.get_user_id())
                return login_user
            else:
                log.debug("login failed: %r" % resp)
                return None
        except Exception as e:
            log.error(e)
            return None

    def __oauth_login(self, provider):
        code = request.args.get('code')
        oauth_data = {
            "code": code,
            "redirect_uri": get_config("endpoint.hackathon_web") + "/" + provider,
            "provider": provider
        }

        return self.__remote_login(oauth_data)

    def __mysql_login(self):

        data = {
            "provider": LOGIN_PROVIDER.DB,
            "username": request.form['username'],
            "password": encode(request.form['password']),
            "code": "user_load"
        }

        return self.__remote_login(data)

    def __remote_login(self, data):
        try:
            req = requests.post(self.login_url, json=data, headers=self.headers)
            resp = req.json()
            if resp:
                # if login isn't successful, it will return None
                login_user = User(resp["user"])
                token = resp["token"]
                log.debug("Login successfully %s" % login_user.get_user_id())
                return {
                    "user": login_user,
                    "token": token["token"]
                }
            else: 
                log.debug("login failed: %r" % resp)
                return None
        except Exception as e:
            log.error(e)
            return None


login_manager_helper = LoginManagerHelper()
