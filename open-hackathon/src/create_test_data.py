#!/usr/bin/python
# -*- coding: utf8 -*-

'''not necessary for Production environment'''

from hackathon.database import db
from hackathon.database.models import HostServer, Announcement


vm = HostServer("localhost", "localhost", 8001, "10.0.2.15", 8001, 0, 100)
# vm = HostServer("osslab-vm-18.chinacloudapp.cn", "osslab-vm-18.chinacloudapp.cn", 8001, "10.210.18.47", 8001, 0, 100)
db.session.add(vm)

#localhost = HostServer("localhost", "localhost", 8001, "10.0.2.15", 8001, 0, 100)
#db.session.add(localhost)

amt = Announcement("欢迎访问开放黑客松平台")
db.session.add(amt)

db.session.commit()