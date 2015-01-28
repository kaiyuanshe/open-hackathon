#!/usr/bin/python
# -*- coding: utf8 -*-

'''not necessary for Production environment'''

from hackathon.database import db
from hackathon.database.models import *


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

r = Register(hackathon=h, register_name="Yifu Huang", email="ifhuang91@gmail.com")

t = Template(hackathon=h, name='ubuntu')
db.session.add(t)

t = Template(hackathon=h, name='rails')
db.session.add(t)

t = Template(hackathon=h, name='mean')
db.session.add(t)

t = Template(hackathon=h, name='python')
db.session.add(t)

t = Template(hackathon=h, name='azure-1', provider='azure',
             url='/home/if/If/LABOSS/open-hackathon/src/hackathon/resources/bigdata-realtime-analytics-azure-1.js')
db.session.add(t)
t = Template(hackathon=h, name='azure-2', provider='azure',
             url='/home/if/If/LABOSS/open-hackathon/src/hackathon/resources/bigdata-realtime-analytics-azure-2.js')
db.session.add(t)

db.session.commit()

