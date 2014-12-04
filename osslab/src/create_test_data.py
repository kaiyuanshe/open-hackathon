from app.database import *

localhost = HostServer("localhost", "localhost", 8001, "10.0.2.15", 8001, 0, 100)
db.session.add(localhost)
db.session.commit()