# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 
The MIT License (MIT)
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import sys

sys.path.append("..")
from hackathon.database import db_adapter
from hackathon.database.models import AdminHackathonRel, User, UserEmail
from flask import g
from hackathon.hackathon_response import *
from hackathon.functions import get_now


class AdminManager(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def get_admin_with_primary_email(self, ids):
        # only returns the primary email
        return self.db.session().query(User, UserEmail). \
            outerjoin(UserEmail, UserEmail.user_id == User.id) \
            .filter(UserEmail.primary_email == 1, UserEmail.user_id.in_(ids)) \
            .all()

    def get_hackathon_admins(self):
        ahls = db_adapter.find_all_objects_by(AdminHackathonRel, hackathon_id=g.hackathon.id)
        user_ids = map(lambda x: x.user_id, ahls)

        def to_dict(user, email):
            dic = user.dic()
            if email is not None:
                dic["email"] = email.dic()
            return dic

        return map(lambda (user, email): to_dict(user, email), self.get_admin_with_primary_email(user_ids))


    def validate_created_args(self, args):
        if 'email' not in args:
            return False, bad_request("email invalid")

        user_email = self.db.find_first_object(UserEmail, UserEmail.email == args['email'])
        if user_email is None:
            return False, not_found("email does not exist")

        uid = user_email.user.id
        hid = g.hackathon.id
        ahl = self.db.find_first_object(AdminHackathonRel, AdminHackathonRel.user_id == uid,
                                        AdminHackathonRel.hackathon_id == hid)
        if ahl is not None:
            return True, 'aleady exist'

        return True, 'passed'


    def create_admin(self, args):
        # validate args
        status, info = self.validate_created_args(args)
        if not status:
            return info
        elif info == 'aleady exist':
            return ok()

        try:
            user_email = self.db.find_first_object(UserEmail, UserEmail.email == args['email'])

            ahl = AdminHackathonRel(user_id=user_email.user.id,
                                    role_type=args['role_type'],
                                    hackathon_id=g.hackathon.id,
                                    status=1,
                                    remarks=args['remarks'],
                                    create_time=get_now())
            self.db.add_object_kwargs(AdminHackathonRel, ahl)
            return ok()
        except Exception as e:
            log.error(e)
            return internal_server_error("create admin failed")


    def update_admin(self):
        return

    def delete_admin(self):
        return


admin_manager = AdminManager(db_adapter)