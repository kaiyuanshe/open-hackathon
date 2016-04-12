# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
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
from user import User
from oauth_login import login_providers


class LoginManagerHelper():
    '''Helper class for flask-login.LoginManager'''
    headers = {"Content-Type": "application/json"}
    login_url = get_config("hackathon-api.endpoint") + "/api/user/login"

    def load_user(self, id):
        try:
            req = requests.get(self.login_url, {"id": id})
            login_user = User(json.loads(req.content))
            return login_user
        except Exception as e:
            log.error(e)
            return None

    def logout(self, token):
        try:
            requests.delete(self.login_url, headers={"token": token})
        except Exception as e:
            log.error(e)

        session.pop("token", "")
        logout_user()

    def login(self, provider):
        if provider == LOGIN_PROVIDER.DB:
            return self.__mysql_login()
        else:
            return self.__oauth_login(provider)

    def __oauth_login(self, provider):
        code = request.args.get('code')
        oauth_resp = login_providers[provider].login({
            "code": code
        })

        return self.__remote_login(oauth_resp)

    def __mysql_login(self):

        data = {
            "provider": LOGIN_PROVIDER.DB,
            "openid": request.form['username'],
            "username": request.form['username'],
            "password": encode(request.form['password'])
        }

        return self.__remote_login(data)

    def __remote_login(self, data):
        try:
            req = requests.post(self.login_url, json=data, headers=self.headers)
            resp = req.json()
            if "error" in resp:
                log.debug("login failed: %r" % resp)
                return None
            else:
                login_user = User(resp["user"])
                token = resp["token"]
                return {
                    "user": login_user,
                    "token": token["token"]
                }
        except Exception as e:
            log.error(e)
            return None


login_manager_helper = LoginManagerHelper()
