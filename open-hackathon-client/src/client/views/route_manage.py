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
from client.functions import is_local


@app.route("/manage/create_event")
@login_required
def create_event():
    return render("/create_event.html", islocal=is_local())

@app.route("/manage")
@login_required
def myhackathon():
    return render("/base/manage.html")

@app.route("/manage/")
@login_required
def myhackathon2():
    return render("/base/manage.html")

@app.route("/manage/<path:path>")
@login_required
def manageddas(path):
    return render("/base/manage.html")

# @app.route("/manage/<hackathon_name>/user")
# @login_required
# def registerusers(hackathon_name):
#     return render("/manage/registerusers.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/azurecert")
# @login_required
# def azurecert(hackathon_name):
#     return render("/manage/azurecert.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/organizers")
# @login_required
# def organizers(hackathon_name):
#     return render("/manage/organizers.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/edit")
# @login_required
# def edithackathon(hackathon_name):
#     return render("/manage/edithackathon.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/notice")
# @login_required
# def hackathon_notice(hackathon_name):
#     return render("/manage/notice.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/template")
# @login_required
# def template(hackathon_name):
#     return render("/manage/template.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/adminmgr")
# @login_required
# def adminmgr(hackathon_name):
#     return render("/manage/adminmgr.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/experiment")
# @login_required
# def experiment(hackathon_name):
#     return render("/manage/experiment.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/team")
# @login_required
# def team(hackathon_name):
#     return render("/manage/team.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/team/<team_id>")
# @login_required
# def team_award(hackathon_name, team_id):
#     return render("/manage/team_award.html", hackathon_name=hackathon_name, team_id=team_id)
#
#
# @app.route("/manage/<hackathon_name>/award")
# @login_required
# def award(hackathon_name):
#     return render("/manage/award.html", hackathon_name=hackathon_name)
#
#
# @app.route("/manage/<hackathon_name>/host_server")
# @login_required
# def host_server(hackathon_name):
#     return render("/manage/host_server.html", hackathon_name=hackathon_name)
