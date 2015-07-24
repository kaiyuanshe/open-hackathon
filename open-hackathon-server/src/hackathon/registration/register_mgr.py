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
from hackathon import Component, RequiredFeature
from flask import g
from hackathon.database.models import UserHackathonRel, Experiment, UserProfile, Team
from hackathon.hackathon_response import bad_request, precondition_failed, internal_server_error, not_found, ok
from hackathon.constants import EStatus, RGStatus, ReservedUser
import json


class RegisterManager(Component):
    hackathon_manager = RequiredFeature("hackathon_manager")
    user_manager = RequiredFeature("user_manager")

    def get_hackathon_registration(self, num=None):
        registers = self.db.find_all_objects_order_by(UserHackathonRel,
                                                      num,  # limit num
                                                      UserHackathonRel.create_time.desc(),
                                                      hackathon_id=g.hackathon.id)
        return map(lambda x: self.get_registration_with_profile(x), registers)

    def get_registration_with_profile(self, register):
        register_dic = register.dic()
        register_dic['user'] = self.user_manager.user_display_info(register.user)
        return register_dic

    def get_registration_by_id(self, id):
        return self.db.get_object(UserHackathonRel, id)

    def get_registration_by_user_and_hackathon(self, user_id, hackathon_id):
        return self.db.find_first_object_by(UserHackathonRel, user_id=user_id, hackathon_id=hackathon_id)

    def check_register_enrollment(self, hackathon):
        max = int(json.loads(hackathon.basic_info)['max_enrollment'])
        if max == 0:  # means no limit
            return True
        else:
            current_num = self.db.count(UserHackathonRel, UserHackathonRel.hackathon_id == hackathon.id)
            return max > current_num

    def validate_created_args(self, hackathon, args):
        self.log.debug("create_register: %r" % args)
        user_id = args['user_id']
        register = self.get_registration_by_user_and_hackathon(user_id, hackathon.id)
        if register is not None and register.deleted == 0:
            self.log.debug("user %d already registered on hackathon %d" % (user_id, hackathon.id))
            return False, register.dic()

        if hackathon.registration_start_time > self.util.get_now():
            return False, precondition_failed("hackathon registration not opened", friendly_message="报名尚未开始")

        if hackathon.registration_end_time < self.util.get_now():
            return False, precondition_failed("hackathon registration has ended", friendly_message="报名已经结束")

        if not self.check_register_enrollment(hackathon):
            return False, precondition_failed("hackathon registers reach the upper threshold",
                                              friendly_message="报名人数已满")
        return True, ""

    def create_registration(self, hackathon, args):
        state, return_info = self.validate_created_args(hackathon, args)
        if not state:
            return return_info
        try:
            args["status"] = hackathon.is_auto_approve() and RGStatus.AUTO_PASSED or RGStatus.UNAUDIT
            return self.db.add_object_kwargs(UserHackathonRel, **args).dic()
        except Exception as e:
            self.log.error(e)
            return internal_server_error("fail to create register")

    def update_registration(self, args):
        self.log.debug("update_registration: %r" % args)
        try:
            id = args['id']
            register = self.get_registration_by_id(id)
            if register is None:
                # we can also create a new object here.
                return not_found("registration not found")

            self.log.debug("update a existed register")
            update_items = dict(dict(args).viewitems() - register.dic().viewitems())
            if "create_time" in update_items:
                update_items.pop("create_time")
            update_items["update_time"] = self.util.get_now()
            self.db.update_object(register, **update_items)

            return register.dic()
        except Exception as e:
            self.log.error(e)
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
            self.log.error(ex)
            return internal_server_error("failed in delete register: %s" % args["id"])

    def get_registration_detail(self, user_id, hackathon):
        detail = {
            "hackathon": hackathon.dic(),
            "user": self.user_manager.user_display_info(g.user)
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
                                                   Experiment.status.in_([EStatus.STARTING, EStatus.RUNNING]))
            if experiment is not None:
                detail["experiment"] = experiment.dic()
        except Exception as e:
            self.log.error(e)

        return detail

    def is_user_registered(self, user_id, hackathon):
        # reservedUser (-1)
        if user_id == ReservedUser.DefaultUserID:
            return True

        # admin
        if self.hackathon_manager.validate_admin_privilege(user_id, hackathon.id):
            return True

        # user
        reg = self.get_registration_by_user_and_hackathon(user_id, hackathon.id)
        if reg is not None:
            return reg.status == RGStatus.AUTO_PASSED or reg.status == RGStatus.AUDIT_PASSED

        return False



    def get_user_profile(self, user_id):
        return self.db.find_first_object_by(UserProfile, user_id=user_id)

    def create_user_profile(self, args):
        self.log.debug("create_user_profile: %r" % args)
        try:
            exist = self.get_user_profile(g.user.id)
            if not exist:
                return self.db.add_object_kwargs(UserProfile, **args).dic()
            else:
                return self.update_user_profile(args)
        except Exception as e:
            self.log.debug(e)
            return internal_server_error("failed to create user profile")

    def update_user_profile(self, args):
        self.log.debug("update_user_profile")
        try:
            u_id = args["user_id"]
            user_profile = self.db.find_first_object_by(UserProfile, user_id=u_id)
            if user_profile:
                self.db.update_object(user_profile, **args)
                return user_profile.dic()
            else:
                return not_found("fail to update user profile")
        except Exception as e:
            self.log.debug(e)
            return internal_server_error("failed to update user profile")
