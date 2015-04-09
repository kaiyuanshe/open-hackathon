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
from datetime import datetime
from hackathon.log import log
from flask import g


class RegisterManger(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def get_register_list(self, hackathon_id):
        # TODO make query result with pagination
        registers = self.db.find_all_objects(Register, Register.hackathon_id == hackathon_id)
        return map(lambda u: u.dic(), registers)

    def get_register_by_id(self, args):
        if "id" not in args:
            return {"error": "Bad request"}, 400
        register = self.db.find_first_object(Register, Register.id == args['id'])
        if register is not None:
            return register.dic()
        else:
            return {"error": "REGISTER NOT FOUND"}, 400

    def create_or_update_register(self, args):
        try:
            register = self.db.find_first_object(Register, Register.email == args['email'],
                                                 Register.hackathon_id == g.hackathon_id)
            if register is None:
                # create a register
                log.debug("create a new register")
                new_register = self.db.add_object_kwargs(Register,
                                                 register_name=args['register_name'],
                                                 email=args['email'],
                                                 create_time=datetime.utcnow(),
                                                 description=args['description'],
                                                 enabled=1,  # 0: disabled 1:enabled
                                                 jstrom_api='',
                                                 jstrom_mgmt_portal='',
                                                 hackathon_id=g.hackathon_id)
                return new_register.dic()
            else:
                # update a aready existe register
                log.debug("update a new register")
                self.db.update_object(register,
                                      register_name=args['register_name'],
                                      email=args['email'],
                                      create_time=datetime.utcnow(),
                                      description=args['description'],
                                      enabled=args['enabled'],  # 0: disabled 1:enabled
                                      strom_api='',
                                      jstrom_mgmt_portal='',
                                      hackathon_id=g.hackathon_id)
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


register_manager = RegisterManger(db_adapter)