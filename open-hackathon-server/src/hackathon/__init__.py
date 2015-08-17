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
from werkzeug.exceptions import HTTPException

__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from datetime import timedelta

from util import safe_get_config, get_class, Utility
from hackathon_factory import factory, RequiredFeature
from hackathon_scheduler import HackathonScheduler
from hackathon_response import *
from log import log
from context import Context

__all__ = [
    "app",
    "Context",
    "RequiredFeature",
    "Component",
]


# initialize flask and flask restful
app = Flask(__name__)
app.config['SECRET_KEY'] = safe_get_config("app.secret_key", "secret_key")
app.debug = True


class HackathonApi(Api):
    """Customize Api to give a chance to handle exceptions in framework level

    We can raise HTTPException and it's inheritances directly in components, they will be caught here. Now we have two
    ways to response with error:
        - return bad_request("some message")
        - raise Bad_Request("some message")
    You can decide to use either way ,they are of the same.
    """

    def handle_error(self, e):
        log.error(e)
        if isinstance(e, HTTPException):
            message = e.description
            if hasattr(e, "data") and "message" in e.data:
                message = e.data["message"]
            if e.code == 400:
                return self.make_response(bad_request(message), 200)
            if e.code == 401:
                return self.make_response(unauthorized(message), 200)
            if e.code == 403:
                return self.make_response(forbidden(message), 200)
            if e.code == 404:
                return self.make_response(not_found(message), 200)
            if e.code == 409:
                return self.make_response(conflict(message), 200)
            if e.code == 412:
                return self.make_response(precondition_failed(message), 200)
            if e.code == 415:
                return self.make_response(unsupported_mediatype(message), 200)
            if e.code == 500:
                return self.make_response(internal_server_error(message), 200)

        # if exception cannot be handled, return error 500
        return self.make_response(internal_server_error(e.message), 200)


# init restful API
api = HackathonApi(app)

# Enable CORS support. Currently requests of all methods from all domains are allowed
app.config['CORS_HEADERS'] = 'Content-Type, token, hackathon_name'
cors = CORS(app)

# initialize hackathon scheduler
scheduler = HackathonScheduler(app)


@app.errorhandler(400)
def bad_request_handler(error):
    log.error(error)
    return bad_request(error.message)


@app.errorhandler(412)
def precondition_failed_handler(error):
    log.error(error)
    return precondition_failed(error.message)


@app.errorhandler(Exception)
def exception_handler(error):
    log.error(error)
    return internal_server_error(error.message)


class Component(object):
    """Base class of business object

    inheritance classes can make use of self.log, self.db and self.util directly without import or instantiating,
    """
    log = RequiredFeature("log")
    db = RequiredFeature("db")
    util = RequiredFeature("util")


def init_components():
    """Init hackathon factory"""
    from hackathon.database import db_session
    from hackathon.database.db_adapters import SQLAlchemyAdapter
    from hackathon.user import UserManager
    from hackathon.azureformation.fileService import FileService
    from hackathon.azureformation.azureCertManagement import AzureCertManagement
    from hackathon.hack import HackathonManager, AdminManager, TeamManager, DockerHostManager
    from hackathon.registration.register_mgr import RegisterManager
    from hackathon.template.template_mgr import TemplateManager
    from hackathon.remote.guacamole import GuacamoleInfo
    from hackathon.expr.expr_mgr import ExprManager
    from hackathon.cache.cache_mgr import CacheManagerExt

    # dependencies MUST be provided in advance
    factory.provide("util", Utility)
    factory.provide("log", log)
    factory.provide("db", SQLAlchemyAdapter, db_session)

    # scheduler
    factory.provide("scheduler", scheduler)

    # business components
    factory.provide("user_manager", UserManager)
    factory.provide("hackathon_manager", HackathonManager)
    factory.provide("register_manager", RegisterManager)
    factory.provide("file_service", FileService)
    factory.provide("azure_cert_management", AzureCertManagement)
    factory.provide("docker_host_manager", DockerHostManager)
    factory.provide("template_manager", TemplateManager)
    factory.provide("expr_manager", ExprManager)
    factory.provide("admin_manager", AdminManager)
    factory.provide("team_manager", TeamManager)
    factory.provide("guacamole", GuacamoleInfo)
    factory.provide("cache", CacheManagerExt)

    # health check items
    factory.provide("health_check_mysql", get_class("hackathon.health.health_check.MySQLHealthCheck"))
    factory.provide("health_check_hosted_docker", get_class("hackathon.health.health_check.HostedDockerHealthCheck"))
    factory.provide("health_check_alauda_docker", get_class("hackathon.health.health_check.AlaudaDockerHealthCheck"))
    factory.provide("health_check_guacamole", get_class("hackathon.health.health_check.GuacamoleHealthCheck"))
    factory.provide("health_check_azure", get_class("hackathon.health.health_check.AzureHealthCheck"))

    # docker
    factory.provide("docker", get_class("hackathon.docker.docker_helper.DockerHelper"))
    factory.provide("hosted_docker", get_class("hackathon.docker.hosted_docker.HostedDockerFormation"))
    factory.provide("alauda_docker", get_class("hackathon.docker.alauda_docker.AlaudaDockerFormation"))

    # storage
    init_hackathon_storage()


def init_hackathon_storage():
    """Add storage implementation to hackathon factory

    The type of storage is configured by ""storage.type"" in config.py which is 'local' by default
    """
    from hackathon.storage import AzureStorage, LocalStorage

    storage_type = safe_get_config("storage.type", "azure")
    if storage_type == "azure":
        factory.provide("storage", AzureStorage)
    else:
        factory.provide("storage", LocalStorage)


def init_schedule_jobs():
    """Init scheduled jobs

    Note that scheduler job will NOT be enabled in main thread. So the real initialization work are completed in a
    separated thread. Otherwise there might be dead lock in main thread.
    """
    if safe_get_config("environment", "local") == "local":
        return

    import threading

    t = threading.Thread(target=__init_schedule_jobs)
    t.start()


def __init_schedule_jobs():
    """Init scheduled jobs in fact"""
    sche = RequiredFeature("scheduler")
    expr_manager = RequiredFeature("expr_manager")

    # schedule job to check recycle operation
    next_run_time = util.get_now() + timedelta(seconds=10)
    sche.add_interval(feature="expr_manager",
                      method="scheduler_recycle_expr",
                      id="scheduler_recycle_expr",
                      next_run_time=next_run_time,
                      minutes=10)

    # schedule job to pre-allocate environment
    expr_manager.schedule_pre_allocate_expr_job()

    # schedule job to pull docker images automatically
    if not safe_get_config("docker.alauda.enabled", False):
        docker = RequiredFeature("hosted_docker")
        docker.ensure_images()


def init_app():
    """Initialize the application.

    Works including :
        - setting up hackathon factory,
        - register restful API routes
        - initialize scheduled jobs
    """
    init_components()

    from views import init_routes
    init_routes()
    init_schedule_jobs()


init_app()
