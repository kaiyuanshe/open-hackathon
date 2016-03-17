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
import json

from flask import g

from hackathon import Component, RequiredFeature
from hackathon.hmongo.models import UserHackathon
from hackathon.database import UserHackathonRel, Experiment, HackathonConfig, UserHackathonAsset
from hackathon.hackathon_response import bad_request, precondition_failed, internal_server_error, not_found, ok, \
    login_provider_error
from hackathon.constants import EStatus, HACK_USER_STATUS, HACKATHON_BASIC_INFO, HACKATHON_STAT, LOGIN_PROVIDER, \
    HACK_USER_TYPE

__all__ = ["RegisterManager"]


class RegisterManager(Component):
    """Component to manage registered users of a hackathon"""
    hackathon_manager = RequiredFeature("hackathon_manager")
    user_manager = RequiredFeature("user_manager")
    admin_manager = RequiredFeature("admin_manager")
    team_manager = RequiredFeature("team_manager")

    def get_hackathon_registration_list(self, num=None):
        """Get registered users list

        :rtype: list
        :return all registered usrs if num is None else return the specific number of users order by create_time desc
        """
        registers = UserHackathon.objects(hackathon=g.hackathon).order_by('-create_time') if not num \
                    else UserHackathon.objects(hackathon=g.hackathon).order_by('-create_time').limit(num)

        return map(lambda x: self.__get_registration_with_profile(x), registers)

    def get_registration_by_id(self, registration_id):
        return self.db.get_object(UserHackathonRel, registration_id)

    def get_registration_by_user_and_hackathon(self, user_id, hackathon_id):
        return UserHackathon.objects(user=user_id, hackathon=hackathon_id).first()

    def create_registration(self, hackathon, user, args):
        """Register hackathon for user

        Will add a new record in table UserRegistrationRel if precondition fulfilled
        """
        self.log.debug("create_register: %r" % args)
        user_id = args['user_id']

        check_login_provider = self.__is_user_hackathon_login_provider(user, hackathon)
        if check_login_provider["fail"]:
            return login_provider_error("hackathon registration not login provider",
                                        friendly_message="当前黑客松活动只是使用"+",".join(check_login_provider["provides"])+"账户才能报名",
                                        provides=",".join(check_login_provider["provides"]))

        if self.is_user_registered(user.id, hackathon):
            self.log.debug("user %d already registered on hackathon %d" % (user_id, hackathon.id))
            return self.get_registration_detail(user, hackathon)

        if self.admin_manager.is_hackathon_admin(hackathon.id, user.id):
            return precondition_failed("administrator cannot register the hackathon", friendly_message="管理员或裁判不能报名")

        if hackathon.registration_start_time and hackathon.registration_start_time > self.util.get_now():
            return precondition_failed("hackathon registration not opened", friendly_message="报名尚未开始")

        if hackathon.registration_end_time and hackathon.registration_end_time < self.util.get_now():
            return precondition_failed("hackathon registration has ended", friendly_message="报名已经结束")

        if self.__is_hackathon_filled_up(hackathon):
            return precondition_failed("hackathon registers reach the upper threshold",
                                       friendly_message="报名人数已满")

        try:
            args["status"] = HACK_USER_STATUS.AUTO_PASSED if hackathon.is_auto_approve() else HACK_USER_STATUS.UNAUDIT
            args['create_time'] = self.util.get_now()
            user_hackathon_rel = self.db.add_object_kwargs(UserHackathonRel, **args).dic()

            # create a team as soon as user registration approved(auto or manually)
            if hackathon.is_auto_approve():
                self.team_manager.create_default_team(hackathon, user)

            self.__update_register_stat(hackathon)
            return user_hackathon_rel
        except Exception as e:
            self.log.error(e)
            return internal_server_error("fail to create register")

    def update_registration(self, context):
        try:
            registration_id = context.id
            register = self.get_registration_by_id(registration_id)
            if register is None or register.hackathon_id != g.hackathon.id:
                # we can also create a new object here.
                return not_found("registration not found")

            register.update_time = self.util.get_now()
            register.status = context.status
            self.db.commit()

            if register.status == HACK_USER_STATUS.AUDIT_PASSED:
                self.team_manager.create_default_team(register.hackathon, register.user)

            hackathon = self.hackathon_manager.get_hackathon_by_id(register.hackathon_id)
            self.__update_register_stat(hackathon)

            return register.dic()
        except Exception as e:
            self.log.error(e)
            return internal_server_error("fail to  update register")

    def delete_registration(self, args):
        """
        Delete the registration of a user in a hackathon, also do operation on the user's team.
        """
        if "id" not in args:
            return bad_request("id not invalid")
        try:
            register = self.db.find_first_object_by(UserHackathonRel, id = args['id'])
            user = register.user
            if register is not None:
                self.db.delete_object(register)
                hackathon = self.hackathon_manager.get_hackathon_by_id(register.hackathon_id)
                self.__update_register_stat(hackathon)

                team = self.team_manager.get_team_by_user_and_hackathon(user, hackathon)
                if not team:
                    self.log.warn("team of this registered user is not found!")
                    return ok()
                self.team_manager.quit_team_forcedly(team, user)

            return ok()
        except Exception as ex:
            self.log.error(ex)
            return internal_server_error("failed in delete register: %s" % args["id"])

    # TODO: registration related functions are to be refactored
    def get_registration_detail(self, user, hackathon):
        detail = {
            "hackathon": hackathon.dic(),
            "user": self.user_manager.user_display_info(user),
            "asset":[]
        }

        # asset = self.db.find_all_objects_by(UserHackathonAsset, user_id=user.id, hackathon_id=hackathon.id)
        # if asset:
        #     detail["asset"] = [o.dic() for o in asset]

        # rel = self.get_registration_by_user_and_hackathon(user.id, hackathon.id)
        # if rel is None:
        #     return detail

        # detail["registration"] = rel.dic()
        # # experiment if any
        # try:
        #     experiment = self.db.find_first_object(Experiment,
        #                                            Experiment.user_id == user.id,
        #                                            Experiment.hackathon_id == hackathon.id,
        #                                            Experiment.status.in_([EStatus.STARTING, EStatus.RUNNING]))
        #     if experiment is not None:
        #         detail["experiment"] = experiment.dic()
        # except Exception as e:
        #     self.log.error(e)

        return detail

    def __update_register_stat(self, hackathon):
        count = self.db.count(UserHackathonRel,
                              UserHackathonRel.hackathon_id == hackathon.id,
                              UserHackathonRel.status.in_([HACK_USER_STATUS.AUDIT_PASSED, HACK_USER_STATUS.AUTO_PASSED]),
                              UserHackathonRel.deleted == 0)
        self.hackathon_manager.update_hackathon_stat(hackathon, HACKATHON_STAT.REGISTER, count)

    def is_user_registered(self, user_id, hackathon):
        """Check whether use registered certain hackathon"""
        register = self.get_registration_by_user_and_hackathon(user_id, hackathon.id)
        return register is not None and register.role == HACK_USER_TYPE.COMPETITOR

    def __get_registration_with_profile(self, registration):
        """Return user display info as well as the registration detail in dict

        :type registration: UserHackathonRel
        :param registration: the detail of the user registration

        :rtype: dict
        :return the detail of registration as well as user display info
        """
        register_dic = registration.dic()
        register_dic['user'] = self.user_manager.user_display_info(registration.user)
        return register_dic

    def __is_hackathon_filled_up(self, hackathon):
        """Check whether all seats are occupied or not

        :return False if not all seats occupied or hackathon has no limit at all otherwise True
        """
        maximum = hackathon.get_basic_property(HACKATHON_BASIC_INFO.MAX_ENROLLMENT, 0)
        if maximum == 0:  # means no limit
            return False
        else:
            # count of audited users
            current_num = self.db.count(UserHackathonRel,
                                        UserHackathonRel.hackathon_id == hackathon.id,
                                        UserHackathonRel.status.in_([HACK_USER_STATUS.AUDIT_PASSED, HACK_USER_STATUS.AUTO_PASSED]))
            return current_num >= max

    def __is_user_hackathon_login_provider(self, user, hackathon):
        """Check whether login prpvoder

        :return False if not all seats occupied or hackathon has no limit at all otherwise True
        """
        login_provider = self.db.find_first_object(HackathonConfig,
                           HackathonConfig.hackathon_id == hackathon.id,
                           HackathonConfig.key == 'login_provider')

        data = {"fail": False, "provides": []}
        hackathon_login_provider = int(login_provider.value)

        if hackathon_login_provider & LOGIN_PROVIDER.LIVE == LOGIN_PROVIDER.LIVE:
            data["provides"].append("live")

        if hackathon_login_provider & LOGIN_PROVIDER.GITHUB == LOGIN_PROVIDER.GITHUB:
            data["provides"].append("github")

        if hackathon_login_provider & LOGIN_PROVIDER.QQ == LOGIN_PROVIDER.QQ:
            data["provides"].append("qq")

        if hackathon_login_provider & LOGIN_PROVIDER.WEIBO == LOGIN_PROVIDER.WEIBO:
            data["provides"].append("weibo")

        if hackathon_login_provider & LOGIN_PROVIDER.GITCAFE == LOGIN_PROVIDER.GITCAFE:
            data["provides"].append("gitcafe")

        if hackathon_login_provider & LOGIN_PROVIDER.ALAUDA == LOGIN_PROVIDER.ALAUDA:
            data["provides"].append("alauda")


        if login_provider is None:
            data["fail"] = False
        elif user.provider in data["provides"]:
            data["fail"] = False
        else:
            data["fail"] = True
        return data