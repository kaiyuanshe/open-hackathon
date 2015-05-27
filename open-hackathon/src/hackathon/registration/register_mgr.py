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
from hackathon.database.models import UserHackathonRel, Experiment
from hackathon.database import db_adapter
from hackathon.hackathon_response import *
from hackathon.functions import get_now
from hackathon.enum import EStatus, RGStatus, ReservedUser
from hackathon.hack import hack_manager


class RegisterManger(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def get_all_registration_by_hackathon_id(self, hackathon_id):
        # TODO make query result with pagination
        registers = self.db.find_all_objects_by(UserHackathonRel, hackathon_id=hackathon_id)
        return [r.dic() for r in registers]

    def get_registration_by_id(self, id):
        return self.db.get_object(UserHackathonRel, id)

    def get_registration_by_user_and_hackathon(self, user_id, hackathon_id):
        return self.db.find_first_object_by(UserHackathonRel, user_id=user_id, hackathon_id=hackathon_id)

    def create_registration(self, hackathon, args):
        log.debug("create_or_update_register: %r" % args)
        if "user_id" not in args:
            return bad_request("user id invalid")

        try:
            user_id = args['user_id']
            register = self.get_registration_by_user_and_hackathon(user_id, hackathon.id)
            if register is not None and register.deleted == 0:
                log.debug("user %d already registered on hackathon %d" % (user_id, hackathon.id))
                return register.dic()

            if hackathon.registration_start_time > get_now():
                return precondition_failed("hackathon registration not opened", friendly_message="报名尚未开始")

            if hackathon.registration_end_time < get_now():
                return precondition_failed("hackathon registration has ended", friendly_message="报名已经结束")

            args["status"] = hackathon.is_auto_approve() and RGStatus.AUTO_PASSED or RGStatus.UNAUDIT

            return self.db.add_object_kwargs(UserHackathonRel, **args).dic()
        except Exception as e:
            log.error(e)
            return internal_server_error("fail to create or update register")


    def update_registration(self, args):
        log.debug("update_registration: %r" % args)
        try:
            id = args['id']
            register = self.get_registration_by_id(id)
            if register is None:
                # we can also create a new object here.
                return not_found("registration not found")

            log.debug("update a existed register")
            update_items = dict(dict(args).viewitems() - register.dic().viewitems())
            if "create_time" in update_items: update_items.pop("create_time")
            update_items["update_time"] = get_now()
            self.db.update_object(register, **update_items)

            return register.dic()
        except Exception as e:
            log.error(e)
            return internal_server_error("fail to  update register")

    def delete_registration(self, args):
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

    def get_registration_detail(self, user_id, hackathon):
        detail = {
            "hackathon": hackathon.dic()
        }

        rel = self.get_registration_by_user_and_hackathon(user_id, hackathon.id)
        if rel is None:
            # return nothing
            return detail

        detail["registration"] = rel.dic()
        # experiment
        try:
            experiment = self.db.find_first_object(Experiment,
                                                   Experiment.user_id == user_id,
                                                   Experiment.hackathon_id == hackathon.id,
                                                   Experiment.status.in_([EStatus.Starting, EStatus.Running]))
            if experiment is not None:
                detail["experiment"] = experiment.dic()
        except Exception as e:
            log.error(e)

        return detail

    def is_email_registered(self, hid, email):
        register = self.db.find_first_object_by(UserHackathonRel, hackathon_id=hid, email=email, deleted=0)
        return register is None

    def is_user_registered(self, user_id, hackathon):
        # reservedUser (-1)
        if user_id == ReservedUser.DefaultUserID:
            return True

        # admin
        if hack_manager.validate_admin_privilege(user_id, hackathon.id):
            return True

        # user
        reg = self.get_registration_by_user_and_hackathon(user_id, hackathon.id)
        if reg is not None:
            return reg.status == RGStatus.AUTO_PASSED or reg.status == RGStatus.AUDIT_PASSED

        return False


register_manager = RegisterManger(db_adapter)
