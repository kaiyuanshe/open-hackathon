from hackathon.database import Base, engine
from hackathon.database.models import AdminGroup,AdminUserGroup
from hackathon.database import db_adapter
from datetime  import datetime
from hackathon.enum import AdminUserGroupStates

def setup_db():
    # initialize db tables
    # make sure database and user correctly created in mysql
    # in case upgrade the table structure, the origin table need be dropped firstly
    Base.metadata.create_all(bind=engine)

    #init db : add a super admin account
    db_adapter.add_object_kwargs(AdminGroup,
                                         id=1,
                                         name="SuperAdmin",
                                         hackathon_id= -1 ,
                                         create_time = datetime.utcnow())

    db_adapter.add_object_kwargs(AdminUserGroup,
                                        id=1,
                                        admin_email='2303202961@qq.com',
                                        state=AdminUserGroupStates.Actived,
                                        remarks='super admins',
                                        create_time = datetime.utcnow(),
                                        group_id=1)
    db_adapter.commit()


setup_db()