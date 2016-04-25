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

import json
import requests
from flask_login import login_required, current_user
from flask import request, session, abort, redirect

from . import render
from client import app, Context
from client.functions import get_config

API_USER= "/api/user"

@app.route("/user/p_<user_id>")
def profile(user_id):
    # current_user is the login-in user, check whether the current user want to view his own profile.
    current_user = Context.from_object(__get_api(API_USER, {"token": session.get("token")}))
    searched_user = Context.from_object(__get_api(API_USER, params={"user_id": user_id}))
    if "id" in current_user and "id" in searched_user and current_user.id == searched_user.id:
        return redirect("/user/profile")
    return render("/user/profile.html")


@app.route("/user/profile")
@login_required
def user_profile():
    return render("/user/profile.html")


@app.route("/user/edit")
@login_required
def user_profile_edit():
    return render("/user/profile_edit.html")


@app.route("/user/picture", methods=['POST'])
@login_required
def user_picture():
    args = request.form
    current_user.avatar_url = args["url"] or current_user.avatar_url
    return "OK"


@app.route("/user/hackathon")
@login_required
def user_hackathon_list():
    return render("/user/team.html")


def __get_api(url, headers=None, **kwargs):
    default_headers = {"content-type": "application/json"}
    if headers is not None and isinstance(headers, dict):
        default_headers.update(headers)
    try:
        req = requests.get(get_config("hackathon-api.endpoint") + url, headers=default_headers, **kwargs)
        resp = req.content
        return json.loads(resp)
    except Exception:
        abort(500, 'API Service is not yet open')
