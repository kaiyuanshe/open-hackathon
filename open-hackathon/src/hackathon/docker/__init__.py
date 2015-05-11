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

import sys

sys.path.append("..")
import json
import requests
from hackathon.log import log
from hackathon.functions import convert
from compiler.ast import flatten
from threading import Lock
from hackathon.database import db_adapter
from hackathon.database.models import Experiment
from hackathon.enum import EStatus


def name_match(id, l):
    for n in l:
        if id in n:
            return True
    return False


default_http_headers = {'content-type': 'application/json'}


class OssDocker(object):
    host_ports = []

    def __init__(self):
        self.lock = Lock()

    def get_vm_url(self, docker_host):
        vm_url = "http://" + docker_host.public_dns + ":" + str(docker_host.public_docker_api_port)
        return vm_url

    def __ports_cache(self):
        """
        cache ports, if ports' number more than 30, release the ports.
        But if there is a thread apply new ports, we will do this operation in the next loop. Because the host machine
        do not update the ports information, if we release ports now, the new ports will be lost.
        """
        num = db_adapter.count(Experiment, Experiment.status == EStatus.Starting)
        if num > 0:
            log.debug("there are %d experiment is starting, host ports will updated in next loop")
            return
        log.debug("-----release ports cache successfully------")
        OssDocker.host_ports = []

    def ping(self, docker_host):
        try:
            ping_url = self.get_vm_url(docker_host) + '/_ping'
            req = requests.get(ping_url)
            log.debug(req.content)
            return req.status_code == 200 and req.content == 'OK'
        except Exception as e:
            log.error(e)
            return False

    def containers_info(self, docker_host):
        try:
            containers_url = self.get_vm_url(docker_host) + "/containers/json"
            req = requests.get(containers_url)
            log.debug(req.content)
            return convert(json.loads(req.content))
        except:
            log.error("cannot get containers' info")
            raise

    def __get_available_host_port(self, port_bindings, port):
        """
        simple lock mechanism, visit static variable ports synchronize, because port_bindings is not in real-time, so we
        should cache the latest ports, when the cache ports number is more than 30, we will release it to save space.
        """
        self.lock.acquire()
        try:
            host_port = port + 10000
            while host_port in port_bindings or host_port in OssDocker.host_ports:
                host_port += 1
            if host_port >= 65535:
                log.error("port used up on this host server")
                raise Exception("no port available")
            if len(OssDocker.host_ports) >= 30:
                self.__ports_cache()
            OssDocker.host_ports.append(host_port)
            log.debug("host_port is %d " % host_port)
            return host_port
        finally:
            self.lock.release()

    def get_available_host_port(self, docker_host, private_port):

        """
        We use double operation to ensure ports not conflicted, first we get ports from host machine, but in multiple
        threads situation, the interval between two requests is too short, maybe the first thread do not get port
        ended, so the host machine don't update ports in time, thus the second thread may get the same port. To
        avoid this condition, we use static variable host_ports to cache the latest 30 ports. Every thread visit
        variable host_ports is synchronized. To save space, we will release the ports if the number over 30.
        """

        log.debug("try to assign docker port %d on server %r" % (private_port, docker_host))
        containers = self.containers_info(docker_host)
        host_ports = flatten(map(lambda p: p['ExposedPorts'], containers))

        # todo if azure return -1
        def sub(port):
            return port["PublicPort"] if "PublicPort" in port else -1

        host_public_ports = map(lambda x: sub(x), host_ports)
        return self.__get_available_host_port(host_public_ports, private_port)

    def get_container(self, name, docker_host):
        containers = self.containers_info(docker_host)
        return next((c for c in containers if name in c["Names"] or '/' + name in c["Names"]), None)

    def search_containers_by_expr_id(self, id, docker_host, all=False):
        get_containers = self.containers_info(docker_host)
        if all:
            return get_containers
        return filter(lambda c: name_match(id, c["Names"]), get_containers)

    def stop(self, name, docker_host):
        """
        stop a container, name is the container's name, docker_host is the host machine where container running
        """
        if self.get_container(name, docker_host) is not None:
            try:
                containers_url = self.get_vm_url(docker_host) + "/containers/%s/stop" % name
                req = requests.post(containers_url)
                log.debug(req.content)
            except:
                log.error("container %s fail to stop" % name)
                raise

    def delete(self, name, docker_host):
        """
        delete a container
        """
        try:
            containers_url = self.get_vm_url(docker_host) + "/containers/%s?force=1" % name
            req = requests.delete(containers_url)
            log.debug(req.content)
        except:
            log.error("container %s fail to stop" % name)
            raise

    def create(self, docker_host, container_config, container_name):
        """
        create a container, https://docs.docker.com/reference/api/docker_remote_api_v1.17/#create-a-container
        only create a container, in this step, we cannot start a container.
        :param docker_host:
        :param container_config:
        :param container_name:
        :return:
        """
        containers_url = self.get_vm_url(docker_host) + "/containers/create?name=%s" % container_name
        try:
            req = requests.post(containers_url, data=json.dumps(container_config), headers=default_http_headers)
            log.debug(req.content)
            container = json.loads(req.content)
        except Exception as err:
            log.error(err)
            raise
        if container is None:
            raise AssertionError("container is none")
        return container

    def start(self, docker_host, container_id, start_config={}):
        """
        start a container, start_config is the configure of container which you want to start, there are often include
        some ports which you want to open.
        for example: start_config = { "PortBindings":{"22/tcp":["10022"]}}, "Binds":[]}
        """
        try:
            url = self.get_vm_url(docker_host) + "/containers/%s/start" % container_id
            req = requests.post(url, data=json.dumps(start_config), headers=default_http_headers)
            log.debug(req.content)
        except:
            log.error("container %s fail to start" % container_id)
            raise

    def run(self, args, docker_host):
        """
        In this function, we create a container and then start a container, args is the container's config
        """
        container_name = args["container_name"]
        exist = self.get_container(container_name, docker_host)
        result = {
            "container_name": container_name
        }
        if exist is not None:
            result["container_id"] = exist["Id"]
        else:
            image = args["Image"]
            # ports foramt: [from, to ,from2, to2]. e.g.[9080,8080,3306,3306].Similar with 'mnts'
            ports = args["docker_ports"] if "docker_ports" in args else []
            port_bingings = dict(zip(ports[1::2], ports[::2]))

            mnts = args["mnt"] if "mnt" in args else []
            mnts_f = map(
                lambda s: s if "%s" not in s or "scm" not in args else s % args["scm"]["local_repo_path"],
                mnts[::2])
            mnts_t = map(lambda s: {"bind": s, "ro": False}, mnts[1::2])
            mnt_bindings = dict(zip(mnts_f, mnts_t))

            command = args["Cmd"] if "Cmd" in args else None
            stdin_open = args["OpenStdin"] if "OpenStdin" in args else False
            tty = args["Tty"] if "Tty" in args else False
            dns = args["dns"] if "dns" in args else None
            entrypoint = args["entrypoint"] if "entrypoint" in args else None
            working_dir = args["working_dir"] if "working_dir" in args else None
            attach_std_in = args["AttachStdin"] if "AttachStdin" in args else False
            attach_std_out = args["AttachStdout"] if "AttachStdout" in args else False
            attach_std_err = args["AttachStderr"] if "AttachStderr" in args else False
            env_variable = args["Env"] if "Env" in args else None

            # headers = {'content-type': 'application/json'}
            container_config = {"Image": image, "ExposedPorts": {}}
            for key in port_bingings:
                container_config["ExposedPorts"][str(key) + "/tcp"] = {}
            if mnts_f:
                for v in mnts_f:
                    container_config["Volumes"] = {}
                    container_config["Volumes"][v] = {}
            container_config["Env"] = env_variable
            if command is not None:
                container_config["Cmd"] = command
            container_config["OpenStdin"] = stdin_open
            container_config["Tty"] = tty
            container_config["Dns"] = dns
            container_config["Entrypoint"] = entrypoint
            container_config["WorkingDir"] = working_dir
            container_config["AttachStdin"] = attach_std_in
            container_config["AttachStdout"] = attach_std_out
            container_config["AttachStderr"] = attach_std_err
            try:
                container = self.create(docker_host, container_config, container_name)
            except Exception as e:
                log.error(e)
                log.error("container %s fail to create" % container_name)
                return None

            # start container
            # start_config = { "PortBindings":{"22/tcp":["10022"]}}, "Binds":[]}
            start_config = {"PortBindings": {}}

            # "Binds" = ["/host/path:/container/path:ro/rw"]
            if mnt_bindings:
                start_config["Binds"] = []
                for key in mnt_bindings:
                    start_config["Binds"].append(key + ":" + mnt_bindings[key]["bind"] + ":rw")
            for key in port_bingings:
                temp = []
                config = {"HostPort": str(port_bingings[key])}
                temp.append(config)
                start_config["PortBindings"][str(key) + "/tcp"] = temp
            result["container_id"] = container["Id"]
            # start container
            try:
                self.start(docker_host, container["Id"], start_config)
            except Exception as e:
                log.error(e)
                log.error("container %s fail to start" % container["Id"])
                return None

            if self.get_container(container_name, docker_host) is None:
                log.error("container %s has started, but can not find it in containers' info, maybe it exited again."
                          % container_name)
                return None

        return result