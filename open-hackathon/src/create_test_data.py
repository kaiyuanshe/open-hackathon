#!/usr/bin/python
# -*- coding: utf8 -*-

'''not necessary for Production environment'''

from hackathon.database import db
from hackathon.database.models import *
from hackathon.log import *
from hackathon.enum import *

# vm = DockerHostServer(vm_name="localhost", public_dns="localhost", public_docker_api_port=8001, private_ip="10.0.2.15",
# private_docker_api_port=8001, container_count=0, container_max_count=100)
# vm = DockerHostServer(vm_name="osslab-vm-20.chinacloudapp.cn", public_dns="osslab-vm-20.chinacloudapp.cn",
#                       public_docker_api_port=8001, private_ip="10.210.18.47", private_docker_api_port=8001,
#                       container_count=0, container_max_count=100)
# db.session.add(vm)

localhost = DockerHostServer(vm_name="localhost", public_dns="localhost", public_docker_api_port=8001,
                             private_ip="10.0.2.15",
                             private_docker_api_port=8001, container_count=0, container_max_count=100)
db.session.add(localhost)

amt = Announcement("欢迎访问开放黑客松平台")
db.session.add(amt)

h = Hackathon("bigdata-realtime-analytics", 1)
db.session.add(h)


db.session.add(Register(hackathon=h, register_name="Yifu Huang", email="ifhuang91@gmail.com"))
db.session.add(Register(hackathon=h, register_name="xxzhe", email="zhengxx012@gmail.com"))
db.session.add(Register(hackathon=h, register_name="junbo", email="juniwang@microsoft.com"))

# add public templates to database
template_dir = 'hackathon/resources'
if not os.path.isdir(template_dir):
    log.error('template dir %s is not exist' % template_dir)
    sys.exit(1)
template_files = os.listdir(template_dir)
if template_files is None:
    log.error('template dir %s is empty' % template_dir)
    sys.exit(1)
for template_file in template_files:
    name = template_file.replace('bigdata-realtime-analytics-', '').replace('.js', '')
    template_url = os.getcwd() + os.path.sep + template_dir + os.path.sep + template_file
    provider = VirtualEnvironmentProvider.Docker
    if 'azure' in name:
        provider = VirtualEnvironmentProvider.AzureVM
    template = Template(hackathon=h, name=name, url=template_url, provider=provider)
    db.session.add(template)

db.session.commit()
