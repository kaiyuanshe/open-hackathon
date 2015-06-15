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
from docker_formation_base import (
    DockerFormationBase
)
from hackathon.constants import (
    HEALTH_STATE,
    ALAUDA_SERVICE_STATUS,
)
from hackathon.enum import (
    VEProvider,
)
from hackathon.hackathon_exception import (
    AlaudaException
)
from hackathon.template.docker_template_unit import (
    DockerTemplateUnit
)
from hackathon import Component
import json
import time
from datetime import datetime, timedelta


class AlaudaDockerFormation(DockerFormationBase, Component):
    def start(self, unit, **kwargs):
        virtual_environment = kwargs["virtual_environment"]

        virtual_environment.provider = VEProvider.Alauda
        self.db.commit()

        service_config = self.__get_service_config(unit)
        self.__create_service(service_config)

        # todo change docker process to async
        service_name = unit.get_name()
        service = self.__query_service(service_name)
        count = 0
        while (service["is_deploying"]):
            self.log.debug('wait for alauda to deploy [%s], wait count [%d]' % (service_name, count))
            count += 1
            if count > 60:  # 10 minutes in total
                self.log.error('Timed out waiting for async operation to complete.')
                return False
            time.sleep(10)
            try:
                service = self.__query_service(service_name)
            except AlaudaException:
                continue

        self.__flush_service_log(service_name)

        if not self.__is_service_started(service):
            raise Exception("fail to start container")

        # guacamole config
        guacamole = unit.get_remote()
        instance_port = filter(lambda p:
                               p["container_port"] == guacamole[DockerTemplateUnit.REMOTE_PORT],
                               service["instance_ports"])
        if len(instance_port) > 0:
            gc = {
                "displayname": service_name,
                "name": service_name,
                "protocol": guacamole[DockerTemplateUnit.REMOTE_PROTOCOL],
                "hostname": instance_port[0]["default_domain"],
                "port": instance_port[0]["service_port"]
            }
            if DockerTemplateUnit.REMOTE_USERNAME in guacamole:
                gc["username"] = guacamole[DockerTemplateUnit.REMOTE_USERNAME]

            if DockerTemplateUnit.REMOTE_PASSWORD in guacamole:
                gc["password"] = guacamole[DockerTemplateUnit.REMOTE_PASSWORD]

            # save guacamole config into DB
            virtual_environment.remote_paras = json.dumps(gc)
            self.db.commit()

        self.log.debug("starting container %s on alauda is succesfull" % (service_name))
        return service

    def stop(self, name, **kwargs):
        """stop a alauda service"""
        virtual_environment = kwargs["virtual_environment"]
        self.__stop_service(virtual_environment.name)
        self.__flush_service_log(virtual_environment.name)

    def delete(self, name, **kwargs):
        """delete a alauda service"""
        virtual_environment = kwargs["virtual_environment"]
        self.__delete_service(virtual_environment.name)
        self.__flush_service_log(virtual_environment.name)

    def health(self):
        """send a ping for health check"""
        try:
            self.__get("/v1/auth/profile/")
            return {
                "status": HEALTH_STATE.OK
            }
        except:
            return {
                "status": HEALTH_STATE.ERROR,
                "description": "request alauda failed"
            }

    # --------------------------------------private function--------------------------#
    def __get_default_service_config(self):
        default_service_config = {
            "service_name": "",
            "namespace": self.util.get_config("docker.alauda.namespace"),
            "image_name": "",
            "image_tag": "latest",
            "run_command": "",
            "instance_size": "XS",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "custom_domain_name": "",
            "linked_to_apps": "{}",
            "target_num_instances": "1",
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

    def __get_service_log(self, service_name):
        namespace = self.util.get_config("docker.alauda.namespace")
        start_time = self.__format_time(datetime.utcnow() + timedelta(hours=-11))
        end_time = self.__format_time(datetime.utcnow() + timedelta(hours=1))
        path = "/v1/services/%s/%s/logs/?start_time=%s&end_time=%s" % (namespace, service_name, start_time, end_time)
        return self.__get(path)

    def __flush_service_log(self, service_name):
        service_logs = self.__get_service_log(service_name)
        message = ["latest logs from alauda:"]

        def sub(li):
            message.append("    %s:  %s" % (datetime.fromtimestamp(li["time"]), li["message"]))

        map(lambda li: sub(li), service_logs)
        self.log.debug("\n".join(message))

    def __create_service(self, config):
        namespace = self.util.get_config("docker.alauda.namespace")
        path = "/v1/services/%s" % namespace
        self.__post(path, config)

    def __start_service(self, service_name):
        namespace = self.util.get_config("docker.alauda.namespace")
        path = "/v1/services/%s/%s/start/" % (namespace, service_name)
        self.__put(path, None)

    def __stop_service(self, service_name):
        namespace = self.util.get_config("docker.alauda.namespace")
        path = "/v1/services/%s/%s/stop/" % (namespace, service_name)
        self.__put(path, None)

    def __delete_service(self, service_name):
        namespace = self.util.get_config("docker.alauda.namespace")
        path = "/v1/services/%s/%s/" % (namespace, service_name)
        self.__delete(path)

    def __query_service(self, service_name):
        namespace = self.util.get_config("docker.alauda.namespace")
        path = "/v1/services/%s/%s/" % (namespace, service_name)
        return self.__get(path)

    def __is_service_started(self, service):
        # todo "target_state" not the running state of service. find out another way to test the status.
        # e.g. ping specific port
        return service["target_state"] == ALAUDA_SERVICE_STATUS.STARTED

    def __format_time(self, date):
        return int(date - datetime(1970, 1, 1, tzinfo=None))

    def __get_full_url(self, path):
        sep = "" if path.startswith("/") else "/"
        base_uri = self.util.safe_get_config("docker.alauda.endpoint", "https://api.alauda.cn")
        return "%s%s%s" % (base_uri, sep, path)

    def __get_headers(self):
        token = self.util.get_config("docker.alauda.token")
        return {
            "Authorization": "Token %s" % token,
            "Content-Type": "application/json"
        }

    def __post(self, path, data):
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.__request("post", path, data)

    def __put(self, path, data):
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.__request("put", path, data)

    def __delete(self, path):
        return self.__request("delete", path)

    def __get(self, path):
        resp = self.__request("get", path)
        return self.util.convert(json.loads(resp))

    def __request(self, method, path, data=None):
        url = self.__get_full_url(path)
        req = requests.request(method, url, headers=self.__get_headers(), data=data)
        if req.status_code >= 200 and req.status_code < 300:
            resp = req.content
            self.log.debug("'%s' response %d from alauda api '%s': %s" % (method, req.status_code, path, resp))
            return resp
        else:
            self.log.debug("'%s' from alauda api '%s' failed: %s, %s" % (method, path, req.status_code, req.content))
            raise AlaudaException(req.status_code, req.content)

