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
from hackathon.database.models import AdminHackathonRel, UserEmail, Hackathon
from hackathon.hackathon_response import bad_request, not_found, internal_server_error, ok, precondition_failed
from hackathon.enum import AdminUserHackathonRelStates
from hackathon import RequiredFeature, Component
from flask import g


class AdminManager(Component):
    user_manager = RequiredFeature("user_manager")

    def get_hackathon_admin_list(self):
        return self.db.find_all_objects_by(AdminHackathonRel, hackathon_id=g.hackathon.id)


    def get_admin_details(self, ahl):
        dic = ahl.dic()
        dic["user_info"] = self.user_manager.user_display_info(ahl.user)
        return dic


    def get_hackathon_admins(self):
        return map(lambda ahl: self.get_admin_details(ahl), self.get_hackathon_admin_list())


    def __validate_created_args(self, args):
        if 'email' not in args:
            return False, bad_request("email invalid")

        return True, ''


    def create_admin(self, args):
        # validate args
        status, resp = self.__validate_created_args(args)
        if not status:
            return resp

        try:
            user_email = self.db.find_first_object(UserEmail, UserEmail.email == args['email'])
            if user_email is None:
                return not_found("email does not exist in DB")

            uid = user_email.user.id
            hid = g.hackathon.id
            ahl = self.db.find_first_object(AdminHackathonRel,
                                            AdminHackathonRel.user_id == uid,
                                            AdminHackathonRel.hackathon_id == hid)
            if ahl is None:
                ahl = AdminHackathonRel(
                    user_id=user_email.user.id,
                    role_type=args['role_type'],
                    hackathon_id=g.hackathon.id,
                    status=AdminUserHackathonRelStates.Actived,
                    remarks=args['remarks'],
                    create_time=self.util.get_now()
                )
                self.db.add_object(ahl)
            return ok()
        except Exception as e:
            self.log.error(e)
            return internal_server_error("create admin failed")


    def validate_updated_args(self, args):
        if 'id' not in args:
            return False, bad_request("invalid id")

        ahl = self.db.find_first_object(AdminHackathonRel, AdminHackathonRel.id == args['id'])
        if ahl is None:
            return False, not_found("ahl does not exist")

        return True, ahl


    def generate_update_items(self, args):
        update_items = {}
        update_items['update_time'] = self.util.get_now()
        if 'role_type' in args:
            update_items['role_type'] = args['role_type']
        if 'remarks' in args:
            update_items['remarks'] = args['remarks']
        return update_items


    def update_admin(self, args):
        status, ahl = self.validate_updated_args(args)
        if not status:
            return ahl

        update_items = self.generate_update_items(args)

        try:
            self.db.update_object(ahl, **update_items)
            return ok('update hackathon admin success')
        except Exception as e:
            self.log.error(e)
            return internal_server_error(e)


    def validate_deleted_args(self, ahl_id):
        ahl = self.db.find_first_object(AdminHackathonRel, AdminHackathonRel.id == ahl_id)
        if ahl is None:
            return False, ok()

        hackathon = self.db.find_first_object(Hackathon, Hackathon.id == ahl.hackathon_id)
        if hackathon.creator_id == ahl.user_id:
            return False, precondition_failed("hackathon creator can not be deleted")

        return True, 'pass'


    def delete_admin(self, ahl_id):
        status, info = self.validate_deleted_args(ahl_id)
        if not status:
            return info
        try:
            self.db.delete_all_objects(AdminHackathonRel, AdminHackathonRel.id == ahl_id)
            return ok()
        except Exception as e:
            self.log.error(e)
            return internal_server_error(e)
