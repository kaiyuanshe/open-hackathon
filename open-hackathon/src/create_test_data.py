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

r = Register(hackathon=h, register_name="junbo", email="juniwang@microsoft.com")
db.session.add(r)

db.session.commit()