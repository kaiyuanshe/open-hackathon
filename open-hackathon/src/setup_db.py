# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#  
# The MIT License (MIT)
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#  
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

from hackathon.database import Base, engine
from hackathon.database.models import AdminUserHackathonRel
from hackathon.database import db_adapter
from datetime import datetime
from hackathon.enum import AdminUserHackathonRelStates
from hackathon.constants import ADMIN


def setup_db():
    # initialize db tables
    # make sure database and user correctly created in mysql
    # in case upgrade the table structure, the origin table need be dropped firstly
    Base.metadata.create_all(bind=engine)

    # init db : add a super admin account
    superadmin = db_adapter.find_first_object_by(AdminUserHackathonRel,
                                                 admin_email=ADMIN.DEFAULT_SUPER_ADMIN_EMAIL,
                                                 hackathon_id=ADMIN.SUPER_ADMIN_GROUP_ID)
    if superadmin is None:
        db_adapter.add_object_kwargs(AdminUserHackathonRel,
                                     admin_email=ADMIN.DEFAULT_SUPER_ADMIN_EMAIL,
                                     hackathon_id=ADMIN.SUPER_ADMIN_GROUP_ID,
                                     state=AdminUserHackathonRelStates.Actived,
                                     remarks='super admins',
                                     create_time=datetime.utcnow())
        db_adapter.commit()


setup_db()