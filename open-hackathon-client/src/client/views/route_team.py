# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")

from client import app
from client.views import render
from flask_login import login_required


@app.route("/team")
@login_required
def team_list():
    return render("/team/index.html")


@app.route("/team/<hackathon_name>")
@login_required
def user_team_hackathon(hackathon_name):
    return render("/team/team.html", hackathon_name=hackathon_name)
