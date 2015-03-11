from hackathon.database import Base, engine
from hackathon.database.models import AdminUserHackathonRel
from hackathon.database import db_adapter
from datetime  import datetime
from hackathon.enum import AdminUserHackathonRelStates

def setup_db():
    # initialize db tables
    # make sure database and user correctly created in mysql
    # in case upgrade the table structure, the origin table need be dropped firstly
    Base.metadata.create_all(bind=engine)

    #init db : add a super admin account
    superadmin = db_adapter.find_first_object(AdminUserHackathonRel,admin_email='2303202961@qq.com',hackathon_id=-1)
    if superadmin is None:
        db_adapter.add_object_kwargs(AdminUserHackathonRel,
                                            admin_email='2303202961@qq.com',
                                            hackathon_id=-1,
                                            state=AdminUserHackathonRelStates.Actived,
                                            remarks='super admins',
                                            create_time = datetime.utcnow())
        db_adapter.commit()

setup_db()