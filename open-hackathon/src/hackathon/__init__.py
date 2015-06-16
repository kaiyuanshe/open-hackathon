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

__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask, g, request
from flask_restful import Api
from flask_cors import CORS
from util import safe_get_config, get_class, Utility
from hackathon_factory import factory, RequiredFeature


# flask
app = Flask(__name__)
app.config['SECRET_KEY'] = safe_get_config("app.secret_key", "secret_key")

# flask restful
api = Api(app)

# CORS
app.config['CORS_HEADERS'] = 'Content-Type, token, hackathon_name'
cors = CORS(app)


class Component(object):
    log = RequiredFeature("log")
    db = RequiredFeature("db")
    util = RequiredFeature("util")


def init_components():
    from hackathon.log import log
    from hackathon.database import db_session
    from hackathon.database.db_adapters import SQLAlchemyAdapter
    from hackathon.user.user_mgr import UserManager
    from hackathon.azureformation.fileService import FileService
    from hackathon.azureformation.azureCertManagement import AzureCertManagement
    from hackathon.hack.host_server_mgr import DockerHostManager
    from hackathon.hack import HackathonManager
    from hackathon.registration.register_mgr import RegisterManger
    from hackathon.template.template_mgr import TemplateManager
    from hackathon.admin.admin_mgr import AdminManager
    from hackathon.remote.guacamole import GuacamoleInfo
    from hackathon.expr.expr_mgr import ExprManager

    # dependencies MUST be provided in advance
    factory.provide("util", Utility)
    factory.provide("log", log)
    factory.provide("db", SQLAlchemyAdapter, db_session)

    factory.provide("user_manager", UserManager)
    factory.provide("hackathon_manager", HackathonManager)
    factory.provide("register_manager", RegisterManger)
    factory.provide("file_service", FileService)
    factory.provide("azure_cert_management", AzureCertManagement)
    factory.provide("docker_host_manager", DockerHostManager)
    factory.provide("template_manager", TemplateManager)
    factory.provide("expr_manager", ExprManager)
    factory.provide("admin_manager", AdminManager)
    factory.provide("guacamole", GuacamoleInfo)

    factory.provide("mysql_health_check", get_class("hackathon.health.health_check.MySQLHealthCheck"))
    factory.provide("docker_health_check", get_class("hackathon.health.health_check.DockerHealthCheck"))
    factory.provide("guacamole_health_check", get_class("hackathon.health.health_check.GuacamoleHealthCheck"))
    factory.provide("azure_health_check", get_class("hackathon.health.health_check.AzureHealthCheck"))

    # factory.provide("docker", get_class("hackathon.docker.docker_helper.DockerHelper"))
    # factory.provide("hosted_docker", get_class("hackathon.docker.hosted_docker.HostedDockerFormation"))
    # factory.provide("alauda_docker", get_class("hackathon.docker.alauda_docker.AlaudaDockerFormation"))
    if safe_get_config("docker.alauda.enabled", False):
        factory.provide("docker", get_class("hackathon.docker.alauda_docker.AlaudaDockerFormation"))
    else:
        factory.provide("docker", get_class("hackathon.docker.hosted_docker.HostedDockerFormation"))


def init_app():
    init_components()

    from views import init_routes

    init_routes()

    from initialise_jobs import start_init_job
    start_init_job()


init_app()