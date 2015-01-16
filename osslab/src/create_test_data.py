from app.database import *

localhost = HostServer("localhost", "osslab.cloudvm.cn", 8001, "10.0.2.15", 8001, 0, 100)
db.session.add(localhost)
db.session.commit()