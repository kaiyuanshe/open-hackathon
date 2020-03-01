# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
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
        req = requests.get(get_config("endpoint.hackathon_api") + url, headers=default_headers, **kwargs)
        resp = req.content
        return json.loads(resp)
    except Exception:
        abort(500, 'API Service is not yet open')
