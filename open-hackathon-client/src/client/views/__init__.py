# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

import sys

sys.path.append("..")

from client import app
import json
from client.constants import LOGIN_PROVIDER
from flask_login import login_required, current_user, login_user, LoginManager
from client.admin.login import login_providers
from client.admin.admin_mgr import admin_manager
from flask import Response, render_template, request, g, redirect, make_response, session
from datetime import timedelta
from client.functions import get_config
from client.log import log

session_lifetime_minutes = 60
PERMANENT_SESSION_LIFETIME = timedelta(minutes=session_lifetime_minutes)

login_manager = LoginManager()
login_manager.init_app(app)


def __oauth_meta_content():
    return {
        LOGIN_PROVIDER.WEIBO: get_config('login.weibo.meta_content'),
        LOGIN_PROVIDER.QQ: get_config('login.qq.meta_content')
    }


def render(template_name_or_list, **context):
    return render_template(template_name_or_list,
                           meta_content=__oauth_meta_content(),
                           **context)


def __login_failed(provider, error="Login failed."):
    if provider == "mysql":
        error = "Login failed. username or password invalid."
    return render("/login.html", error=error)


def __login(provider):
    code = request.args.get('code')
    try:
        admin_with_token = login_providers[provider].login({
            "code": code
        })
        if admin_with_token is None:
            return __login_failed(provider)

        log.info("login successfully:" + repr(admin_with_token))

        token = admin_with_token["token"].token
        login_user(admin_with_token["admin"])
        session["token"] = token
        resp = make_response(redirect("/manage"))
        resp.set_cookie('token', token)
        return resp
    except Exception as ex:
        log.error(ex)
        return __login_failed(provider)


@login_manager.user_loader
def load_user(id):
    return admin_manager.get_admin_by_id(id)


@app.before_request
def before_request():
    g.admin = current_user
    app.permanent_session_lifetime = timedelta(minutes=session_lifetime_minutes)


@app.errorhandler(401)
def custom_401(error):
    return render("/login.html", error=None)


# js config
@app.route('/config.js')
def js_config():
    resp = Response(response="var CONFIG=%s" % json.dumps(get_config("javascript")),
                    status=200,
                    mimetype="application/javascript")
    return resp


@app.route('/github')
def github_login():
    return __login(LOGIN_PROVIDER.GITHUB)


@app.route('/weibo')
def weibo_login():
    return __login(LOGIN_PROVIDER.WEIBO)


@app.route('/qq')
def qq_login():
    return __login(LOGIN_PROVIDER.QQ)


@app.route('/gitcafe')
def gitcafe_login():
    return __login(LOGIN_PROVIDER.GITCAFE)


@app.route('/live')
def live_login():
    return __login(LOGIN_PROVIDER.LIVE)


@app.route('/')
@app.route('/index')
def index():
    return render('/home.html')


@app.route('/help')
def help():
    return render('/help.html')


@app.route('/about')
def about():
    return render('/about.html')


@app.route("/logout")
@login_required
def logout():
    login_providers.values()[0].logout(g.admin)
    return redirect("/login")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return __login(LOGIN_PROVIDER.MYSQL)

    # todo redirect to the page request login

    return render("/login.html", error=None)


from route_manage import *
from route_template import *
from route_user import *