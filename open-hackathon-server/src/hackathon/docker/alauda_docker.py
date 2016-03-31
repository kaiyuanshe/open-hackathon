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
import requests
import json
from datetime import datetime, timedelta

from docker_formation_base import DockerFormationBase
from hackathon.constants import HEALTH_STATUS, VE_PROVIDER, VEStatus, EStatus, HEALTH, OAUTH_PROVIDER
from hackathon.hmongo.models import VirtualEnvironment
from hackathon.hackathon_exception import AlaudaException
from hackathon.template import DOCKER_UNIT
from hackathon import Component, Context, RequiredFeature


class ALAUDA:
    IS_DEPLOYING = "is_deploying"
    CURRENT_STATUS = "current_status"
    RUNNING = "Running"
    CONTAINER_PORT = "container_port"
    INSTANCE_PORTS = "instance_ports"
    DEFAULT_DOMAIN = "default_domain"
    SERVICE_PORT = "service_port"


class AlaudaDockerFormation(DockerFormationBase, Component):
    user_manager = RequiredFeature("user_manager")
    expr_manager = RequiredFeature("expr_manager")

    def start(self, unit, **kwargs):
        virtual_environment = kwargs["virtual_environment"]
        user = virtual_environment.experiment.user

        virtual_environment.provider = VE_PROVIDER.ALAUDA
        self.db.commit()

        service_config = self.__get_service_config(unit)
        self.__create_service(user, service_config)

        service_name = unit.get_name()
        service = self.__query_service(user, service_name)
        # service = {}

        context = Context(guacamole=unit.get_remote(),
                          service_name=service_name,
                          user_id=user.id,
                          virtual_environment_id=virtual_environment.id,
                          ve_remote_paras=virtual_environment.remote_paras)
        self.__service_result_handler(service, context)
        return service

    def stop(self, name, **kwargs):
        """stop a alauda service"""
        virtual_environment = kwargs["virtual_environment"]
        user = virtual_environment.experiment.user
        self.__stop_service(user, virtual_environment.name)

    def delete(self, name, **kwargs):
        """delete a alauda service"""
        virtual_environment = kwargs["virtual_environment"]
        user = virtual_environment.experiment.user
        self.__delete_service(user, virtual_environment.name)

    def report_health(self):
        """send a ping for health check"""
        try:
            namespace = self.util.get_config("docker.alauda.namespace")
            token = self.util.get_config("docker.alauda.token")
            headers = {
                "Authorization": "Token %s" % token,
                "Content-Type": "application/json"
            }
            path = "/v1/auth/%s/profile/" % namespace
            self.__request("get", path, headers=headers)
            return {
                HEALTH.STATUS: HEALTH_STATUS.OK
            }
        except Exception as e:
            self.log.error(e)
            return {
                HEALTH.STATUS: HEALTH_STATUS.ERROR,
                HEALTH.DESCRIPTION: "request alauda failed"
            }

    # --------------------------------------private function--------------------------#
    def __schedule_query_service_status(self, context):
        self.log.debug("alauda service '%r' is deploying, will query again 10 seconds later" % context)
        self.scheduler.add_once("alauda_docker", "query_service_status_async", context=context, seconds=10)

    def __service_result_handler(self, service, context):
        if self.__is_service_deploying(service):
            self.__schedule_query_service_status(context)
        elif self.__is_service_running(service):
            self.__service_started_handler(service, context)
        else:
            self.__service_failed_handler(context)

    def query_service_status_async(self, context):
        try:
            user = self.__get_user_by_context(context)
            service = self.__query_service(user, context.service_name)
            self.__service_result_handler(service, context)
        except AlaudaException as ae:
            self.log.error(ae)
            self.log.debug(
                "error in query alauda service '%s', will query again 10 seconds later" % context.service_name)
            self.__service_failed_handler(context)

    def __service_started_handler(self, service, context):
        service_name = context.service_name
        user = self.__get_user_by_context(context)
        self.__flush_service_log(user, service_name)
        ve = self.db.find_first_object_by(VirtualEnvironment, id=context.virtual_environment_id)
        if not ve:
            self.log.warn("virtual environment cannot be found by id:" + context.virtual_environment_id)
            return

        # update virtual environment status and remote config
        ve.status = VEStatus.RUNNING
        guacamole = context.guacamole
        instance_ports = filter(lambda p:
                                p[ALAUDA.CONTAINER_PORT] == guacamole[DOCKER_UNIT.REMOTE_PORT],
                                service[ALAUDA.INSTANCE_PORTS])
        if len(instance_ports) > 0:
            alauda_port = instance_ports[0]
            gc = {
                "displayname": service_name,
                "name": service_name,
                "protocol": guacamole[DOCKER_UNIT.REMOTE_PROTOCOL],
                "hostname": alauda_port.get(ALAUDA.DEFAULT_DOMAIN),
                "port": alauda_port.get(ALAUDA.SERVICE_PORT),
                "enable-sftp": True
            }

            if DOCKER_UNIT.REMOTE_USERNAME in guacamole:
                gc["username"] = guacamole[DOCKER_UNIT.REMOTE_USERNAME]

            if DOCKER_UNIT.REMOTE_PASSWORD in guacamole:
                gc["password"] = guacamole[DOCKER_UNIT.REMOTE_PASSWORD]

            # save guacamole config into DB
            ve.remote_paras = json.dumps(gc)
        self.db.commit()
        self.expr_manager.on_docker_completed(ve)
        # update experiment status
        self.expr_manager.check_expr_status(ve.experiment)

    def __service_failed_handler(self, context):
        user = self.__get_user_by_context(context)
        self.__flush_service_log(user, context.service_name)
        ve = self.db.find_first_object_by(VirtualEnvironment, id=context.virtual_environment_id)
        if ve:
            # todo rollback
            ve.status = VEStatus.FAILED
            ve.experiment.status = EStatus.FAILED
            self.db.commit()

    def __get_user_by_context(self, context):
        return self.user_manager.get_user_by_id(context.user_id)

    def __get_default_service_config(self):
        default_service_config = {
            "service_name": "",
            "image_name": "",
            "image_tag": "latest",
            "run_command": "",
            "instance_size": "XS",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "custom_domain_name": "",
            "linked_to_apps": "{}",
            "target_num_instances": "1",
            "region_name": self.util.safe_get_config("docker.alauda.region_name", "SHANGHAI1"),
            "instance_envvars": {},
            "instance_ports": [],
            "volumes": []  # todo volumes not implemented for now
        }
        return default_service_config

    def __get_service_config(self, unit):
        service_config = self.__get_default_service_config()
        service_config["service_name"] = unit.get_name()
        service_config["image_name"] = unit.get_image_without_tag()
        service_config["image_tag"] = unit.get_tag()
        service_config["run_command"] = unit.get_run_command()
        service_config["instance_envvars"] = unit.get_instance_env_vars()
        service_config["instance_ports"] = unit.get_instance_ports()
        return service_config

    def __get_service_log(self, user, service_name):
        namespace = self.__get_namespace(user)
        start_time = self.__format_time(datetime.utcnow() + timedelta(hours=-11))
        end_time = self.__format_time(datetime.utcnow() + timedelta(hours=1))
        path = "/v1/services/%s/%s/logs/?start_time=%s&end_time=%s" % (namespace, service_name, start_time, end_time)
        return self.__get(user, path)

    def __flush_service_log(self, user, service_name):
        service_logs = self.__get_service_log(user, service_name)
        message = ["latest logs from alauda:"]

        def sub(li):
            message.append("    %s:  %s" % (datetime.fromtimestamp(li["time"]), li["message"]))

        map(lambda li: sub(li), service_logs)
        self.log.debug("\n".join(message))

    def __create_service(self, user, config):
        namespace = self.__get_namespace(user)
        path = "/v1/services/%s" % namespace
        self.__post(user, path, config)

    def __start_service(self, user, service_name):
        namespace = self.__get_namespace(user)
        path = "/v1/services/%s/%s/start/" % (namespace, service_name)
        self.__put(user, path, None)

    def __stop_service(self, user, service_name):
        namespace = self.__get_namespace(user)
        path = "/v1/services/%s/%s/stop/" % (namespace, service_name)
        self.__put(user, path, None)

    def __delete_service(self, user, service_name):
        namespace = self.__get_namespace(user)
        path = "/v1/services/%s/%s/" % (namespace, service_name)
        self.__delete(user, path)

    def __query_service(self, user, service_name):
        namespace = self.__get_namespace(user)
        path = "/v1/services/%s/%s/" % (namespace, service_name)
        return self.__get(user, path)

    def __is_service_running(self, service):
        return service[ALAUDA.CURRENT_STATUS] == ALAUDA.RUNNING

    def __is_service_deploying(self, service):
        if ALAUDA.IS_DEPLOYING not in service:
            self.log.debug("is_deploying not included in alauda API response. Will retry")
            return True

        return service[ALAUDA.IS_DEPLOYING]

    def __format_time(self, date):
        return int((date - datetime(1970, 1, 1, tzinfo=None)).total_seconds())

    def __get_full_url(self, path):
        sep = "" if path.startswith("/") else "/"
        base_uri = self.util.safe_get_config("docker.alauda.endpoint", "https://api.alauda.cn")
        return "%s%s%s" % (base_uri, sep, path)

    def __get_namespace(self, user):
        if user.provider == OAUTH_PROVIDER.ALAUDA:
            return user.name
        else:
            return self.util.get_config("docker.alauda.namespace")

    def __get_token(self, user):
        if user.provider == OAUTH_PROVIDER.ALAUDA:
            return "Bearer %s" % user.access_token
        return "Token %s" % self.util.get_config("docker.alauda.token")

    def __get_headers(self, user):
        return {
            "Authorization": self.__get_token(user),
            "Content-Type": "application/json"
        }

    def __post(self, user, path, data):
        headers = self.__get_headers(user)
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.__request("post", path, headers=headers, data=data)

    def __put(self, user, path, data):
        headers = self.__get_headers(user)
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.__request("put", path, headers=headers, data=data)

    def __delete(self, user, path):
        headers = self.__get_headers(user)
        return self.__request("delete", path, headers=headers)

    def __get(self, user, path):
        headers = self.__get_headers(user)
        resp = self.__request("get", path, headers=headers)
        return self.util.convert(json.loads(resp))

    def __request(self, method, path, headers=None, data=None):
        url = self.__get_full_url(path)
        req = requests.request(method, url, headers=headers, data=data)
        if 200 <= req.status_code < 300:
            resp = req.content
            self.log.debug("'%s' response %d from alauda api '%s': %s" % (method, req.status_code, path, resp))
            return resp
        else:
            self.log.debug("'%s' from alauda api '%s' failed: %s, %s" % (method, path, req.status_code, req.content))
            raise AlaudaException(req.status_code, req.content)
