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
    Register,
    Hackathon,
    AzureKey,
    HackathonAzureKey,
    Template,
    Announcement,
    DockerHostServer,
)
from hackathon.functions import (
    get_config,
)
from hackathon.log import (
    log,
)
from hackathon.enum import (
    VEProvider,
)
from os.path import (
    realpath,
    dirname,
)
import sys
import os


db_adapter.add_object_kwargs(Announcement, content="欢迎访问开放黑客松平台")

hackathon_name = 'open-xml-sdk'
h = db_adapter.add_object_kwargs(Hackathon, name=hackathon_name, check_register=0, end_time="2016-03-16 00:00:00")

# load azure key
a = db_adapter.add_object_kwargs(AzureKey,
                                 pem_url=get_config('azure.certPath'),
                                 subscription_id=get_config('azure.subscriptionId'),
                                 management_host=get_config('azure.managementServiceHostBase'))
db_adapter.commit()

# associate hackathon with azure key
db_adapter.add_object_kwargs(HackathonAzureKey, hackathon=h, azure_key=a)
db_adapter.commit()

db_adapter.add_object_kwargs(DockerHostServer,
                             vm_name="OSSLAB-VM-18",
                             public_dns="osslab-vm-18.chinacloudapp.cn",
                             public_ip="139.217.0.232",
                             public_docker_api_port=4243,
                             private_ip="10.210.18.47",
                             private_docker_api_port=4243,
                             container_count=0,
                             container_max_count=100,
                             hackathon=h)

db_adapter.add_object_kwargs(Register, hackathon=h, register_name="Yifu Huang", email="ifhuang91@gmail.com")
db_adapter.add_object_kwargs(Register, hackathon=h, register_name="xxzhe", email="zhengxx012@gmail.com")
db_adapter.add_object_kwargs(Register, hackathon=h, register_name="Ice", email="v-iceshi@microsoft.com")

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
    if hackathon_name in template_file:
        name = template_file.replace(hackathon_name + '-', '').replace('.js', '')
        template_url = template_dir + os.path.sep + template_file
        provider = VEProvider.Docker
        if name == 'windows':
            provider = VEProvider.AzureVM
        db_adapter.add_object_kwargs(Template,
                                     name=name,
                                     url=template_url,
                                     provider=provider,
                                     hackathon=h)

db_adapter.commit()
