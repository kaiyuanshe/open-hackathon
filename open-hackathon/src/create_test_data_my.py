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

"""not necessary for Production environment"""

from hackathon.database import (
    db_adapter,
)
from hackathon.database.models import (
    UserHackathonRel,
    Hackathon,
    AzureKey,
    HackathonAzureKey,
    Template,
    Announcement,
    DockerHostServer,
)
from hackathon.log import (
    log,
)
from hackathon.enum import (
    VEProvider,
)
from hackathon.constants import (
    HACKATHON_BASIC_INFO,
)
from os.path import (
    realpath,
    dirname,
)
from datetime import (
    datetime,
    timedelta,
)
import sys
import os
import json


# test announcement
announcement = Announcement(content="欢迎访问开放黑客松平台")
db_adapter.add_object(announcement)


# test hackathon
hackathon = Hackathon(name="open-xml-sdk", display_name="open hackathon", description="description",
                      event_start_time=datetime.utcnow(), event_end_time=datetime.utcnow() + timedelta(days=365),
                      registration_start_time=datetime.utcnow(),
                      registration_end_time=datetime.utcnow() + timedelta(days=365),
                      judge_start_time=datetime.utcnow(), judge_end_time=datetime.utcnow() + timedelta(days=365),
                      basic_info=json.dumps({
                          HACKATHON_BASIC_INFO.AUTO_APPROVE: 1,
                          HACKATHON_BASIC_INFO.RECYCLE_ENABLED: 0
                      }),
                      status=1)
db_adapter.add_object(hackathon)


# test azure key
pem_url = '/home/if/If/open-hackathon/open-hackathon/src/hackathon/certificates/azureformation.pem'
subscription_id = '7946a60d-67b1-43f0-96f9-1c558a9d284c'
management_host = 'management.core.chinacloudapi.cn'
azure_key = AzureKey(pem_url=pem_url,
                     subscription_id=subscription_id,
                     management_host=management_host)
db_adapter.add_object(azure_key)


# associate hackathon with azure key
db_adapter.add_object_kwargs(HackathonAzureKey, hackathon=hackathon, azure_key=azure_key)


# test docker host server
docker_host = DockerHostServer(vm_name="OSSLAB-VM-19", public_dns="osslab-vm-19.chinacloudapp.cn",
                               public_ip="42.159.97.143", public_docker_api_port=4243, private_ip="10.209.14.33",
                               private_docker_api_port=4243, container_count=0, container_max_count=100,
                               hackathon=hackathon)
db_adapter.add_object(docker_host)


# associate user with hackathon
db_adapter.add_object_kwargs(UserHackathonRel, hackathon=hackathon, email="ifhuang91@gmail.com")
db_adapter.add_object_kwargs(UserHackathonRel, hackathon=hackathon, email="zhengxx012@gmail.com")
db_adapter.add_object_kwargs(UserHackathonRel, hackathon=hackathon, email="v-iceshi@microsoft.com")


# add public templates to database
template_dir = dirname(realpath(__file__)) + '/hackathon/resources'
if not os.path.isdir(template_dir):
    log.error('template dir %s is not exist' % template_dir)
    sys.exit(1)
template_files = os.listdir(template_dir)
if template_files is None:
    log.error('template dir %s is empty' % template_dir)
    sys.exit(1)
for template_file in template_files:
    if hackathon.name in template_file:
        name = template_file.replace(hackathon.name + '-', '').replace('.js', '')
        template_url = template_dir + os.path.sep + template_file
        provider = VEProvider.Docker
        if name == 'windows':
            provider = VEProvider.AzureVM
        template = Template(name=name,
                            url=template_url,
                            provider=provider,
                            status=1,
                            virtual_environment_count=1,
                            description='',
                            hackathon=hackathon)
        if db_adapter.find_first_object_by(Template, name=template.name, hackathon_id=hackathon.id) is None:
            db_adapter.add_object(template)

db_adapter.commit()