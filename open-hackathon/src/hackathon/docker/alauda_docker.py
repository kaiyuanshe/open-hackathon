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

import requests
from docker_formation_base import (
    DockerFormationBase
)
from hackathon.constants import (
    HEALTH_STATE,
)
from hackathon.enum import (
    VEProvider,
)
from hackathon.database.models import (
    VirtualEnvironment,
)
from hackathon import Component
import json


class AlaudaDockerFormation(DockerFormationBase, Component):
    def start(self, unit, **kwargs):
        virtual_environment = kwargs["virtual_environment"]
        hackathon = kwargs["hackathon"]
        experiment = kwargs["experiment"]

        virtual_environment.provider = VEProvider.Alauda
        self.db.commit()

        container_name = unit.get_name()
        host_server = self.docker_host_manager.get_available_docker_host(1, hackathon)

        container = DockerContainer(experiment,
                                    name=container_name,
                                    host_server_id=host_server.id,
                                    virtual_environment=virtual_environment,
                                    image=unit.get_image())
        self.db.add_object(container)
        self.db.commit()

        # port binding
        ps = map(lambda p:
                 [p.port_from, p.port_to],
                 self.__assign_ports(experiment, host_server, virtual_environment, unit.get_ports()))

        # guacamole config
        guacamole = unit.get_remote()
        port_cfg = filter(lambda p:
                          p[DockerTemplateUnit.PORTS_PORT] == guacamole[DockerTemplateUnit.REMOTE_PORT],
                          unit.get_ports())
        if len(port_cfg) > 0:
            gc = {
                "displayname": container_name,
                "name": container_name,
                "protocol": guacamole[DockerTemplateUnit.REMOTE_PROTOCOL],
                "hostname": host_server.public_ip,
                "port": port_cfg[0]["public_port"]
            }
            if DockerTemplateUnit.REMOTE_USERNAME in guacamole:
                gc["username"] = guacamole[DockerTemplateUnit.REMOTE_USERNAME]
            if DockerTemplateUnit.REMOTE_PASSWORD in guacamole:
                gc["password"] = guacamole[DockerTemplateUnit.REMOTE_PASSWORD]
            # save guacamole config into DB
            virtual_environment.remote_paras = json.dumps(gc)

        exist = self.__get_container(container_name, host_server)
        if exist is not None:
            container.container_id = exist["Id"]
            host_server.container_count += 1
            self.db.commit()
        else:
            container_config = unit.get_container_config()
            # create container
            try:
                container_create_result = self.__create(host_server, container_config, container_name)
            except Exception as e:
                self.log.error(e)
                self.log.error("container %s fail to create" % container_name)
                return None
            container.container_id = container_create_result["Id"]
            # start container
            try:
                self.__start(host_server, container_create_result["Id"])
                host_server.container_count += 1
                self.db.commit()
            except Exception as e:
                self.log.error(e)
                self.log.error("container %s fail to start" % container["Id"])
                return None
            # check
            if self.__get_container(container_name, host_server) is None:
                self.log.error(
                    "container %s has started, but can not find it in containers' info, maybe it exited again."
                    % container_name)
                return None

        self.log.debug("starting container %s is ended ... " % container_name)
        return container

    def stop(self, name, **kwargs):
        """stop a docker container"""
        return

    def delete(self, name, **kwargs):
        """delete a docker container"""
        return

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
            "image_tag": "",
            "run_command": "",
            "instance_size": "XS",
            "scaling_mode": "MANUAL",
            "target_state": "STARTED",
            "custom_domain_name": "",
            "linked_to_apps": "{}",
            "target_num_instances": "1",
            "instance_envvars": {},
            "instance_ports": []
        }
        return default_service_config

    def __get_service_config(self, unit):
        return {}

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
        return self.__request("post", path, data)

    def __put(self, path, data):
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
            self.log.debug("'%s' response from alauda api '%s': %s" % (method, path, resp))
            return resp
        else:
            self.log.debug("'%s' from alauda api '%s' failed: %s, %s" % (method, path, req.status_code, req.content))
            raise Exception("Http request failed: " + req.content)

