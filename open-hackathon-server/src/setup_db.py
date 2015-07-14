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
from hackathon.database.models import AdminHackathonRel, User
from hackathon.database import db_adapter
from hackathon.util import get_now
from hackathon.constants import ADMIN_ROLE_TYPE, ReservedUser


def setup_db():
    """Initialize db tables

    make sure database and user correctly created in mysql
    in case upgrade the table structure, the origin table need be dropped firstly
    """
    Base.metadata.create_all(bind=engine)

    # init REQUIRED db data.

    # reserved user
    res_u = db_adapter.get_object(User, ReservedUser.DefaultUserID)
    if res_u is None:
        db_adapter.add_object_kwargs(User, id=ReservedUser.DefaultUserID, create_time=get_now())

    # default super admin
    if db_adapter.get_object(User, ReservedUser.DefaultSuperAdmin) is None:
        db_adapter.add_object_kwargs(User, id=ReservedUser.DefaultSuperAdmin, name="admin", nickname="admin",
                                     password="e8104164dfc4a479e42a9f6c0aefd2be")

    # default admin privilege
    if db_adapter.find_first_object_by(AdminHackathonRel, user_id=ReservedUser.DefaultSuperAdmin,
                                       hackathon_id=-1) is None:
        db_adapter.add_object_kwargs(AdminHackathonRel, user_id=ReservedUser.DefaultSuperAdmin,
                                     hackathon_id=-1, role_type=ADMIN_ROLE_TYPE.ADMIN)


setup_db()