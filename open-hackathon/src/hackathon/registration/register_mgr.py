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

import sys

sys.path.append("..")
from hackathon.database.models import UserHackathonRel, UserEmail
from hackathon.database import db_adapter
from hackathon.log import log
from hackathon.hackathon_response import *
from datetime import datetime


class RegisterManger(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def get_all_register_by_hackathon_id(self, hackathon_id):
        # TODO make query result with pagination
        registers = self.db.find_all_objects(UserHackathonRel, UserHackathonRel.hackathon_id == hackathon_id)
        return [r.dic() for r in registers]

    def get_register_by_id(self, id):
        return self.db.get_object(UserHackathonRel, id)

    def create_or_update_register(self, hackathon_id, args):
        log.debug("create_or_update_register: %r" % args)
        if "user_id" not in args:
            return bad_request("user id invalid")

        try:
            user_id = args['user_id']
            register = self.db.find_first_object_by(UserHackathonRel, user_id=user_id, hackathon_id=hackathon_id)
            if register is None:
                log.debug("create a new register")
                return self.db.add_object_kwargs(UserHackathonRel, **args)
            else:
                log.debug("update a existed register")
                update_items = dict(dict(args).viewitems() - register.dic().viewitems())
                update_items.pop("id")
                update_items.pop("create_time")
                update_items["update_time"] = datetime.utcnow()
                self.db.update_object(register, **update_items)
                return register
        except Exception as  e:
            log.error(e)
            return internal_server_error("fail to create or update register")

    def delete_register(self, args):
        if "id" not in args:
            return bad_request("id not invalid")
        try:
            register = self.db.find_first_object_by(UserHackathonRel, id == args['id'])
            if register is not None:
                self.db.delete_object(register)
            return ok()
        except Exception as ex:
            log.error(ex)
            return internal_server_error("failed in delete register: %s" % args["id"])


    def get_register_by_user_id(self, user_id, hackathon_id):
        return self.db.find_first_object_by(UserHackathonRel, user_id == user_id, hackathon_id == hackathon_id)


    def get_register_by_rid_or_uid_and_hid(self, args):
        if 'rid' in args:
            register = self.get_register_by_id(args['rid'])
        elif 'uid' in args and 'hid' in args:
            register = self.get_register_by_user_id(args['uid'], args['hid'])
        else:
            return bad_request("either register id or user id is required")

        if register is None:
            return not_found("register cannot be found by args: %r" % args)
        else:
            return register.dic()


    def check_email(self, hid, email):
        register = self.db.find_first_object_by(UserHackathonRel, hackathon_id=hid, email=email)
        return register is None


register_manager = RegisterManger(db_adapter)
