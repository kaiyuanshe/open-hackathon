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

from flask import g

from hackathon import Component, RequiredFeature
from hackathon.database import AdminHackathonRel, User
from hackathon.constants import ADMIN_ROLE_TYPE
from hackathon.hackathon_response import precondition_failed, ok, not_found, internal_server_error, bad_request

__all__ = ["AdminManager"]


class AdminManager(Component):
    """Component to access/control administrators and judges of hackathon

    Operations related to table AdminHackathonRel should be in this file
    """
    user_manager = RequiredFeature("user_manager")
    hackathon_manager = RequiredFeature("hackathon_manager")

    def validate_admin_privilege(self, user_id, hackathon_id):
        """Check the admin authority on hackathon

        :type user_id: int
        :param user_id: id of an user

        :type hackathon_id: int
        :param hackathon_id: id of a hackathon

        :rtype: bool
        :return True if specific user has admin privilidge on specific hackathon otherwise False
        """
        hack_ids = self.get_entitled_hackathon_ids(user_id)
        return -1 in hack_ids or hackathon_id in hack_ids

    def validate_admin_privilege_http(self):
        """Check the admin authority on hackathon for http request

        Which means both user_id and hackathon_id are come from http request headers. So token and hackathon_name must
        be included in headers and must be validated before calling this method

        :rtype: bool
        :return True if specific user has admin privilidge on specific hackathon otherwise False
        """
        return self.validate_admin_privilege(g.user.id, g.hackathon.id)

    def get_entitled_hackathon_ids(self, user_id):
        """Get hackathon id list that specific user is entitled to manage

        :type user_id: int
        :param user_id: id of user

        :rtype: list
        :return list of hackathon id
        """
        # get AdminUserHackathonRels from query withn filter by email
        admin_user_hackathon_rels = self.db.find_all_objects_by(AdminHackathonRel, user_id=user_id)

        # get hackathon_ids_from AdminUserHackathonRels details
        hackathon_ids = [x.hackathon_id for x in admin_user_hackathon_rels]

        return list(set(hackathon_ids))

    def get_admins_by_hackathon(self, hackathon):
        """Get all admins of a hackathon

        :type hackathon: Hackathon
        :param hackathon: instance of Hackathon

        :rtype: list
        :return list of administrators including the detail information
        """
        rels = self.db.find_all_objects_by(AdminHackathonRel, hackathon_id=hackathon.id)

        def get_admin_details(ahl):
            dic = ahl.dic()
            dic["user_info"] = self.user_manager.user_display_info(ahl.user)
            return dic

        return map(lambda ahl: get_admin_details(ahl), rels)

    def add_admin(self, args):
        """Add a new administrator on a hackathon

        :type args: dict
        :param args: http request body in json format

        :return hackathon response 'ok' if successfully added.
            'not_found' if email is invalid or user not found.
            'internal_server_error' if any other unexpected exception caught
        """
        user = self.user_manager.get_user_by_email(args.get("email"))
        if user is None:
            return not_found("user not found")

        try:
            ahl = self.db.find_first_object(AdminHackathonRel,
                                            AdminHackathonRel.user_id == user.id,
                                            AdminHackathonRel.hackathon_id == g.hackathon.id)
            if ahl is None:
                ahl = AdminHackathonRel(
                    user_id=user.id,
                    role_type=args.get("role_type", ADMIN_ROLE_TYPE.ADMIN),
                    hackathon_id=g.hackathon.id,
                    remarks=args.get("remarks"),
                    create_time=self.util.get_now()
                )
                self.db.add_object(ahl)
            return ok()
        except Exception as e:
            self.log.error(e)
            return internal_server_error("create admin failed")

    def delete_admin(self, ahl_id):
        """Delete admin on a hackathon

        creator of the hackathon cannot be deleted.

        :returns ok() if succeeds or it's deleted before.
                 precondition_failed if try to delete the creator
        """
        ahl = self.db.find_first_object(AdminHackathonRel, AdminHackathonRel.id == ahl_id)
        if not ahl:
            return ok()

        hackathon = self.hackathon_manager.get_hackathon_by_id(ahl.hackathon_id)
        if hackathon and hackathon.creator_id == ahl.user_id:
            return precondition_failed("hackathon creator can not be deleted")

        self.db.delete_all_objects(AdminHackathonRel, AdminHackathonRel.id == ahl_id)
        return ok()

    def update_admin(self, args):
        """Update hackathon admin

        :returns ok() if updated successfully
                 bad_request() if "id" not in request body
                 not_found() if specific AdminHackathonRel not found
                 internal_server_error() if DB exception raised
        """
        id = args.get("id", None)
        if not id:
            return bad_request("invalid id")

        ahl = self.db.find_first_object(AdminHackathonRel, AdminHackathonRel.id == id)
        if not ahl:
            return not_found("admin does not exist")

        update_items = self.__generate_update_items(args)
        try:
            self.db.update_object(ahl, **update_items)
            return ok('update hackathon admin successfully')
        except Exception as e:
            self.log.error(e)
            return internal_server_error(e)

    def is_hackathon_admin(self, hackathon_id, user):
        """Check whether user is admin of specific hackathon

        :type hackathon_id: int
        :param hackathon_id: id of hackathon

        :type user: User
        :param user: the user to be checked

        :rtype: bool
        :return True if user is admin of the hackathon otherwise False
        """
        ahr = self.db.find_first_object_by(AdminHackathonRel, hackathon_id=hackathon_id, user_id=user.id)
        return ahr is not None

    def __generate_update_items(self, args):
        """Generate columns of AdminHackathonRel to be updated"""
        update_items = {}
        update_items['update_time'] = self.util.get_now()
        if 'role_type' in args:
            update_items['role_type'] = args['role_type']
        if 'remarks' in args:
            update_items['remarks'] = args['remarks']
        return update_items
