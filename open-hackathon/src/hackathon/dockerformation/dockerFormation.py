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

from hackathon.log import (
    log,
)
from hackathon.functions import (
    convert,
)
from hackathon.database import (
    db_adapter,
)
from hackathon.database.models import (
    Experiment,
)
from hackathon.enum import (
    EStatus,
)
from compiler.ast import (
    flatten,
)
from threading import (
    Lock,
)
import json
import requests


class DockerFormation(object):
    """
    Docker resource management based on docker remote api v1.18
    """
    application_json = {'content-type': 'application/json'}
    host_ports = []
    host_port_max_num = 30

    def __init__(self):
        self.lock = Lock()

    def ping(self, docker_host):
        try:
            ping_url = '%s/_ping' % self.__get_vm_url(docker_host)
            req = requests.get(ping_url)
            log.debug(req.content)
            return req.status_code == 200 and req.content == 'OK'
        except Exception as e:
            log.error(e)
            return False

    def get_available_host_port(self, docker_host, private_port):
        """
        We use double operation to ensure ports not conflicted, first we get ports from host machine, but in multiple
        threads situation, the interval between two requests is too short, maybe the first thread do not get port
        ended, so the host machine don't update ports in time, thus the second thread may get the same port.
        To avoid this condition, we use static variable host_ports to cache the latest host_port_max_num ports.
        Every thread visit variable host_ports is synchronized.
        To save space, we will release the ports if the number over host_port_max_num.
        :param docker_host:
        :param private_port:
        :return:
        """
        log.debug("try to assign docker port %d on server %r" % (private_port, docker_host))
        containers = self.__containers_info(docker_host)
        host_ports = flatten(map(lambda p: p['ports'], containers))

        # todo if azure return -1
        def sub(port):
            return port["PublicPort"] if "PublicPort" in port else -1

        host_public_ports = map(lambda x: sub(x), host_ports)
        return self.__get_available_host_port(host_public_ports, private_port)

    def stop(self, name, docker_host):
        """
        stop a container
        :param name: container's name
        :param docker_host: host machine where container running
        :return:
        """
        if self.__get_container(name, docker_host) is not None:
            try:
                containers_url = '%s/containers/%s/stop' % (self.__get_vm_url(docker_host), name)
                req = requests.post(containers_url)
                log.debug(req.content)
            except:
                log.error("container %s fail to stop" % name)
                raise

    def delete(self, name, docker_host):
        """
        delete a container
        :param name:
        :param docker_host:
        :return:
        """
        try:
            containers_url = '%s/containers/%s?force=1' % (self.__get_vm_url(docker_host), name)
            req = requests.delete(containers_url)
            log.debug(req.content)
        except:
            log.error("container %s fail to stop" % name)
            raise

    def run(self, unit, docker_host):
        """
        In this function, we create a container and then start a container
        :param unit: docker template unit
        :param docker_host:
        :return:
        """
        container_name = unit.get_name()
        exist = self.__get_container(container_name, docker_host)
        result = {
            "container_name": container_name
        }
        if exist is not None:
            result["container_id"] = exist["Id"]
        else:
            container_config = unit.get_container_config()
            # create container
            try:
                container = self.__create(docker_host, container_config, container_name)
            except Exception as e:
                log.error(e)
                log.error("container %s fail to create" % container_name)
                return None
            result["container_id"] = container["Id"]
            # start container
            try:
                self.__start(docker_host, container["Id"])
            except Exception as e:
                log.error(e)
                log.error("container %s fail to start" % container["Id"])
                return None
            # check
            if self.__get_container(container_name, docker_host) is None:
                log.error("container %s has started, but can not find it in containers' info, maybe it exited again."
                          % container_name)
                return None
        return result

    # --------------------------------------------- helper function ---------------------------------------------#

    def __name_match(self, id, lists):
        for list in lists:
            if id in list:
                return True
        return False

    def __get_vm_url(self, docker_host):
        return 'http://%s:%d' % (docker_host.public_dns, docker_host.public_docker_api_port)

    def __clear_ports_cache(self):
        """
        cache ports, if ports' number more than host_port_max_num, release the ports.
        But if there is a thread apply new ports, we will do this operation in the next loop.
        Because the host machine do not update the ports information,
        if we release ports now, the new ports will be lost.
        :return:
        """
        num = db_adapter.count(Experiment, Experiment.status == EStatus.Starting)
        if num > 0:
            log.debug("there are %d experiment is starting, host ports will updated in next loop" % num)
            return
        log.debug("-----release ports cache successfully------")
        self.host_ports = []

    def __containers_info(self, docker_host):
        try:
            containers_url = '%s/containers/json' % self.__get_vm_url(docker_host)
            req = requests.get(containers_url)
            log.debug(req.content)
            return convert(json.loads(req.content))
        except:
            log.error("cannot get containers' info")
            raise

    def __get_available_host_port(self, port_bindings, port):
        """
        simple lock mechanism, visit static variable ports synchronize, because port_bindings is not in real-time,
        so we should cache the latest ports, when the cache ports number is more than host_port_max_num,
        we will release it to save space.
        :param port_bindings:
        :param port:
        :return:
        """
        self.lock.acquire()
        try:
            host_port = port + 10000
            while host_port in port_bindings or host_port in self.host_ports:
                host_port += 1
            if host_port >= 65535:
                log.error("port used up on this host server")
                raise Exception("no port available")
            if len(self.host_ports) >= self.host_port_max_num:
                self.__clear_ports_cache()
            self.host_ports.append(host_port)
            log.debug("host_port is %d " % host_port)
            return host_port
        finally:
            self.lock.release()

    def __get_container(self, name, docker_host):
        containers = self.__containers_info(docker_host)
        return next((c for c in containers if name in c["Names"] or '/' + name in c["Names"]), None)

    def __search_containers_by_expr_id(self, id, docker_host, all=False):
        get_containers = self.__containers_info(docker_host)
        if all:
            return get_containers
        return filter(lambda c: self.__name_match(id, c["Names"]), get_containers)

    def __create(self, docker_host, container_config, container_name):
        """
        only create a container, in this step, we cannot start a container.
        :param docker_host:
        :param container_config:
        :param container_name:
        :return:
        """
        containers_url = '%s/containers/create?name=%s' % (self.__get_vm_url(docker_host), container_name)
        try:
            req = requests.post(containers_url, data=json.dumps(container_config), headers=self.application_json)
            log.debug(req.content)
            container = json.loads(req.content)
        except Exception as err:
            log.error(err)
            raise
        if container is None:
            raise AssertionError("container is none")
        return container

    def __start(self, docker_host, container_id):
        """
        start a container
        :param docker_host:
        :param container_id:
        :return:
        """
        try:
            url = '%s/containers/%s/start' % (self.__get_vm_url(docker_host), container_id)
            req = requests.post(url, headers=self.application_json)
            log.debug(req.content)
        except:
            log.error("container %s fail to start" % container_id)
            raise


docker_formation = DockerFormation()