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
from flask_login import login_required


@app.route("/user/profile")
@login_required
def user_profile():
    return render("/user/profile.html")


@app.route("/user/hackathon")
@login_required
def user_hackathon_list():
    return render("/user/hackathon.html")


@app.route("/hackathon/<hackathon_name>")
def hackathon_detail(hackathon_name):
    return render("/user/hackathon.html")


# choose a template to start hackathon
@app.route("/hackathon/<hackathon_name>/select")
@login_required
def settings(hackathon_name):
    return render("/register/edit.html")


@app.route("/hackathon/<hackathon_name>/work")
@login_required
def hackathon_workspace(hackathon_name):
    return render("/register/edit.html")


@app.route("/register/<hackathon_name>")
@login_required
def register(hackathon_name):
    return render("/register/profile.html")


