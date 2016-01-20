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

from client import app
from . import render
from flask_login import login_required, current_user
from flask import request


@app.route("/user/p_<user_id>")
def profile(user_id):
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
    args = request.get_json()
    current_user.avatar_url = args["url"] or current_user.avatar_url


@app.route("/user/hackathon")
@login_required
def user_hackathon_list():
    return render("/user/team.html")
