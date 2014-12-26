from app.database import *

vm = HostServer("localhost", "localhost", 8001, "10.0.2.15", 8001, 0, 100)
#vm = HostServer("osslab-vm-18.chinacloudapp.cn", "osslab-vm-18.chinacloudapp.cn", 8001, "10.210.18.47", 8001, 0, 100)
db.session.add(vm)
db.session.commit()