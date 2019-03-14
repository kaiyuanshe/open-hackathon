# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")

from client import app
from . import render
from flask_login import login_required


@app.route("/template")
def template_index():
    return render("/template/index.html")


@app.route("/template/create")
@login_required
def template_create():
    return render("/template/create.html")


@app.route("/template/create/<template_id>")
@login_required
def template_create_from_existing(template_id):
    return render("/template/create.html", template_id=template_id)


@app.route("/template/edit/<template_id>")
def template_edit():
    return render("/template/create.html")


@app.route("/template/try/<template_id>")
@login_required
def try_template(template_id):
    return render("/manage/testtemplate.html")
