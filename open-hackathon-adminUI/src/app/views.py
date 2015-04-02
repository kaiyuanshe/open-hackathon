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

from . import app
from decorators import role_required
from constants import ROLE, OAUTH_PROVIDER
import json
from constants import HTTP_HEADER
from flask_login import login_required, current_user, login_user, LoginManager, logout_user
from admin.login import login_providers
from admin.admin_mgr import admin_manager
from flask import Response, render_template, request, g, redirect, make_response, session, abort
from datetime import timedelta
from functions import safe_get_config, post_to_remote, delete_remote, get_remote, put_to_remote, get_config
from log import log

session_lifetime_minutes = 60
PERMANENT_SESSION_LIFETIME = timedelta(minutes=session_lifetime_minutes)

login_manager = LoginManager()
login_manager.init_app(app)

Template_Routes = {
    "error": "error.html"
}


def __oauth_meta_content():
    return {
        OAUTH_PROVIDER.WEIBO: get_config('login.weibo.meta_content'),
        OAUTH_PROVIDER.QQ: get_config('login.qq.meta_content')
    }


def __get_headers(hackathon_id):
    return {
        "content-type": "application/json",
        HTTP_HEADER.TOKEN: session[HTTP_HEADER.TOKEN] if HTTP_HEADER.TOKEN in session else "",
        HTTP_HEADER.HACKATHON_ID: hackathon_id
    }


def __render(template_name_or_list, **context):
    return render_template(template_name_or_list,
                           meta_content=__oauth_meta_content(),
                           **context)


def __get_uri(path):
    if path.startswith("/"):
        path = path.lstrip("/")
    return "%s/%s" % (safe_get_config('hackathon-api.endpoint', 'http://localhost:15000'), path)


def __login(provider):
    code = request.args.get('code')
    if code is None:
        return "Bad Request", 400

    try:
        admin = login_providers[provider].login({
            "code": code
        })
        login_user(admin)
        return make_response(redirect("/"))
    except:
        return "Internal Server Error", 500


def post_to_api_service(path, post_data, hackathon_id):
    return post_to_remote(__get_uri(path), post_data, headers=__get_headers(hackathon_id))


def put_to_api_service(path, post_data, hackathon_id):
    return put_to_remote(__get_uri(path), post_data, headers=__get_headers(hackathon_id))


def get_from_api_service(path, hackathon_id):
    return get_remote(__get_uri(path), headers=__get_headers(hackathon_id))


def delete_from_api_service(path, hackathon_id):
    return delete_remote(__get_uri(path), headers=__get_headers(hackathon_id))


@login_manager.user_loader
def load_user(id):
    return admin_manager.get_admin_by_id(id)


@app.before_request
def before_request():
    g.admin = current_user
    app.permanent_session_lifetime = timedelta(minutes=session_lifetime_minutes)


def simple_route(path):
    if Template_Routes.has_key(path):
        return render_template(Template_Routes[path],
                               meta_content=__oauth_meta_content())
    else:
        log.warn("page '%s' not found" % path)
        abort(404)

@app.route('/<path:path>')
def template_routes(path):
    return simple_route(path)

# js config
@app.route('/config.js')
def js_config():
    resp = Response(response="var CONFIG=%s" % json.dumps(get_config("javascript")),
                    status=200,
                    mimetype="application/javascript")
    return resp


@app.route('/github')
def github_login():
    return __login(OAUTH_PROVIDER.GITHUB)


@app.route('/weibo')
def weibo_login():
    return __login(OAUTH_PROVIDER.WEIBO)


@app.route('/qq')
def qq_login():
    return __login(OAUTH_PROVIDER.QQ)


@app.route('/gitcafe')
def gitcafe_login():
    return __login(OAUTH_PROVIDER.GITCAFE)


@app.route('/')
@app.route('/index')
def index():
    if g.admin.is_authenticated():
        return redirect("/home")
    return __render('/login.html')


@app.route("/logout")
@login_required
def logout():
    login_providers.values()[0].logout(g.admin)
    logout_user()
    return redirect("/login")

@app.route("/login")
def login():
    return __render("/login.html")

@app.route("/home")
@login_required
def home():
    return __render("/home.html")

@app.route("/users")
@login_required
def users():
    return __render("/users.html")