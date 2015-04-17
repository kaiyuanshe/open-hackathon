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
from hackathon.database.models import *
from hackathon.database import db_adapter
from hackathon.log import log


class RegisterManger(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def get_register_list(self, hackathon_id):
        # TODO make query result with pagination
        registers = self.db.find_all_objects(Register, Register.hackathon_id == hackathon_id)
        return map(lambda u: u.dic(), registers)

    def get_register_by_id(self, id):
        register = self.db.find_first_object(Register, Register.id == args['id'])
        if register is not None:
            return register.dic()
        else:
            return {}

    def create_or_update_register(self, hackathon_id, args):
        try:
            register = self.db.find_first_object(Register, Register.email == args['email'],
                                                 Register.hackathon_id == hackathon_id)
            if register is None:
                # create a register
                log.debug("create a new register")
                # new_register = self.db.add_object_kwargs(Register,
                #                                  register_name=args['register_name'],
                #                                  email=args['email'],
                #                                  create_time=datetime.utcnow(),
                #                                  description=args['description'],
                #                                  enabled=1,  # 0: disabled 1:enabled
                #                                  hackathon_id=g.hackathon_id)
                new_register = self.db.add_object_kwargs(Register, **args)
                return new_register.dic()
            else:
                # update a aready existe register
                log.debug("update a new register")
                update_items = dict(dict(args).viewitems() - register.dic().viewitems())
                # self.db.update_object(register,
                #                       register_name=args['register_name'],
                #                       email=args['email'],
                #                       create_time=datetime.utcnow(),
                #                       description=args['description'],
                #                       enabled=args['enabled'],  # 0: disabled 1:enabled
                #                       hackathon_id=g.hackathon_id)
                self.db.update_object(register, **update_items)
                return register.dic()
        except Exception:
            log.error("create or update register faild")
            return {"error": "INTERNAL SERVER ERROR"}, 500

    def delete_register(self, args):
        if "id" not in args:
            return {"error": "Bad request"}, 400
        try:
            register = self.db.find_first_object(Register, Register.id == args['id'])
            if register is None:
                return {"message": "already removed"}, 200
            self.db.delete_object(register)
        except Exception:
            log.error("delete register faild")
            return {"error": "INTERNAL SERVER ERROR"}, 500

    def get_register_after_login(self, **kwargs):
        hack_id = kwargs['hackathon_id']
        user_id = kwargs['user_id']
        register = db_adapter.find_first_object(Register, Register.hackathon_id == hack_id, Register.user_id == user_id)
        return register

    def check_email(self, hid, email):
        register = db_adapter.find_first_object(Register, Register.hackathon_id == hid, Register.email == email)
        return register is None

    def get_register_by_uid_or_rid_and_hid(self,args):

        # situation One : only rid is given
        # situation Two : uid and hid are both given
        # situation Three : error , bad request

        if args['rid'] is not None:
            return self.get_register_by_id(args['rid'])

        elif args['uid'] is not None and args['hid'] is not None:
            register = db_adapter.find_first_object(Register,Register.user_id==args['uid'],Register.hackathon_id==args['hid'])
            if register is None:
                return {}
            else:
                return register.dic()
        else:
            return {"errorcode":400,"message":"bad request"}



register_manager = RegisterManger(db_adapter)