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

from hackathon import Component, RequiredFeature
from hackathon.database.models import DockerHostServer


class DockerHostManager(Component):

    docker = RequiredFeature("docker")

    def get_available_docker_host(self, req_count, hackathon):
        vms = self.db.find_all_objects(DockerHostServer,
                                       DockerHostServer.container_count + req_count <=
                                       DockerHostServer.container_max_count,
                                       DockerHostServer.hackathon_id == hackathon.id)
        # todo connect to azure to launch new VM if no existed VM meet the requirement
        # since it takes some time to launch VM,
        # it's more reasonable to launch VM when the existed ones are almost used up.
        # The new-created VM must run 'cloudvm service by default(either cloud-init or python remote ssh)
        # todo the VM public/private IP will change after reboot, need sync the IP in db with azure in this case
        for docker_host in vms:
            if self.docker.ping_passed(docker_host):
                return docker_host
        raise Exception("No available VM.")


    def get_host_server_by_id(self, id):
        return self.db.find_first_object_by(DockerHostServer, id=id)

