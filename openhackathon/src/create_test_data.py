#!/usr/bin/python
# -*- coding: utf8 -*-

from hackathon.database import *

#localhost = HostServer("localhost", "localhost", 8001, "10.0.2.15", 8001, 0, 100)
#db.session.add(localhost)

amt = Announcement("欢迎访问开放黑客松平台")
db.session.add(amt)

db.session.commit()