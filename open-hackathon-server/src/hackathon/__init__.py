# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

from werkzeug.exceptions import HTTPException

__author__ = 'Junbo Wang'
__version__ = '2.0'

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from datetime import timedelta

from hackathon.util import safe_get_config, get_class, Utility, Email, DisabledVoiceVerify, RonglianVoiceVerify, DisabledSms, \
    ChinaTelecomSms
from hackathon.hackathon_factory import factory, RequiredFeature
from hackathon.hackathon_scheduler import HackathonScheduler
from hackathon.hackathon_response import *
from hackathon.hackathon_exception import *
from hackathon.log import log
from hackathon.context import Context

__all__ = [
    "app",
    "Context",
    "RequiredFeature",
    "Component",
]

# initialize flask and flask restful
app = Flask(__name__)
app.config['SECRET_KEY'] = safe_get_config("app.secret_key", "secret_key")


class HackathonApi(Api):
    """Customize Api to give a chance to handle exceptions in framework level.
    So that our restful APIs will always respond with code 200 even if Exception thrown and not caught in our codes

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


@app.before_request
def before_request():
    user_manager = RequiredFeature("user_manager")
    user_manager.update_user_operation_time()


class Component(object):
    """Base class of business object

    inheritance classes can make use of self.log, self.db and self.util directly without import or instantiating,
    """
    log = RequiredFeature("log")
    db = RequiredFeature("db")
    util = RequiredFeature("util")
    scheduler = RequiredFeature("scheduler")
    cache = RequiredFeature("cache")


def init_components():
    """Init hackathon factory"""
    from hackathon.user import UserManager, UserProfileManager, OAuthLoginManager
    from hackathon.hack import HackathonManager, AdminManager, TeamManager, DockerHostManager, \
        RegisterManager, HackathonTemplateManager, Cryptor
    from hackathon.template import TemplateLibrary
    from hackathon.remote.guacamole import GuacamoleInfo
    from hackathon.cache.cache_mgr import CacheManagerExt

    # dependencies MUST be provided in advance
    factory.provide("util", Utility)
    factory.provide("log", log)
    init_db()

    # utils
    init_voice_verify()
    init_sms()
    factory.provide("email", Email)

    # cache
    factory.provide("cache", CacheManagerExt)

    # scheduler
    factory.provide("scheduler", scheduler)

    # business components
    factory.provide("user_manager", UserManager)
    factory.provide("user_profile_manager", UserProfileManager)
    factory.provide("oauth_login_manager", OAuthLoginManager)
    factory.provide("hackathon_manager", HackathonManager)
    factory.provide("register_manager", RegisterManager)
    factory.provide("cryptor", Cryptor)
    factory.provide("docker_host_manager", DockerHostManager)
    factory.provide("hackathon_template_manager", HackathonTemplateManager)
    factory.provide("template_library", TemplateLibrary)
    factory.provide("admin_manager", AdminManager)
    factory.provide("team_manager", TeamManager)
    factory.provide("guacamole", GuacamoleInfo)

    # experiment starter
    init_expr_components()

    # health check items
    factory.provide("health_check_hosted_docker", get_class("hackathon.health.health_check.HostedDockerHealthCheck"))
    factory.provide("health_check_guacamole", get_class("hackathon.health.health_check.GuacamoleHealthCheck"))
    factory.provide("health_check_mongodb", get_class("hackathon.health.health_check.MongoDBHealthCheck"))

    # docker
    factory.provide("hosted_docker_proxy", get_class("hackathon.docker.hosted_docker.HostedDockerFormation"))

    # storage
    init_hackathon_storage()


def init_db():
    from .hmongo import db
    factory.provide("db", db, suspend_callable=True)


def init_expr_components():
    from .expr import ExprManager
    factory.provide("expr_manager", ExprManager)


def init_voice_verify():
    """ initial voice verify service
    Example for config.py:
    "voice_verify": {
        "enabled": True,
        "provider": "rong_lian",
        "rong_lian": {
            ... ...
        }
    }
    """
    provider_name = safe_get_config("voice_verify.provider", None)
    enabled = safe_get_config("voice_verify.enabled", False)
    if not enabled:
        log.warn("voice verify disabled")
        factory.provide("voice_verify", DisabledVoiceVerify)
    elif provider_name and safe_get_config("voice_verify." + provider_name, None):
        log.warn("Voice verify initialized to:" + provider_name)
        # if provider other than Ronglian is supported, update following lines
        factory.provide("voice_verify", RonglianVoiceVerify)
    else:
        log.warn("either voice verify provider name or provider config is missing, Please check your configuration")
        raise ConfigurationException("voice_verify.provider")


def init_sms():
    """ initial SMS service """
    provider_name = safe_get_config("sms.provider", None)
    enabled = safe_get_config("sms.enabled", False)
    if not enabled:
        log.warn("SMS service disabled")
        factory.provide("sms", DisabledSms)
    elif provider_name and safe_get_config("sms." + provider_name, None):
        log.warn("SMS initialized to:" + provider_name)
        # if provider other than ChinaTelecom is supported, update following lines
        factory.provide("sms", ChinaTelecomSms)
    else:
        log.warn("Either SMS provider name or provider config is missing, Please check your configuration")
        raise ConfigurationException("sms.provider")


def init_hackathon_storage():
    from hackathon.storage import LocalStorage
    factory.provide("storage", LocalStorage)


def init_schedule_jobs():
    """Init scheduled jobs

    Note that scheduler job will NOT be enabled in main thread. So the real initialization work are completed in a
    separated thread. Otherwise there might be dead lock in main thread.
    """
    import threading

    t = threading.Thread(target=__init_schedule_jobs)
    t.start()


def __init_schedule_jobs():
    """Init scheduled jobs in fact"""
    log.debug("init scheduled jobs......")

    util = RequiredFeature("util")
    sche = RequiredFeature("scheduler")
    if not util.is_local():
        hackathon_manager = RequiredFeature("hackathon_manager")

        # schedule job to check recycle operation
        next_run_time = util.get_now() + timedelta(seconds=10)
        sche.add_interval(feature="expr_manager",
                          method="scheduler_recycle_expr",
                          id="scheduler_recycle_expr",
                          next_run_time=next_run_time,
                          minutes=10)

        # schedule job to pre-allocate environment
        hackathon_manager.schedule_pre_allocate_expr_job()

        # schedule job to pre-create a docker host server VM
        # host_server_manager.schedule_pre_allocate_host_server_job()
    # init the overtime-sessions detection to update users' online status
    sche.add_interval(feature="user_manager",
                      method="check_user_online_status",
                      id="check_user_online_status",
                      minutes=10)


def init_app():
    """Initialize the application.

    Works including :
        - setting up hackathon factory,
        - register restful API routes
        - initialize scheduled jobs
    """
    init_components()

    from .views import init_routes
    init_routes()
    init_schedule_jobs()

    health_check_guacamole = RequiredFeature("health_check_guacamole")
    u = RequiredFeature("util")
    if u.is_local():
        log.debug("guacamole status: %s" % health_check_guacamole.report_health())


init_app()
