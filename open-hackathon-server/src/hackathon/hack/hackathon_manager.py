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
import json
import imghdr
import uuid
import time

from werkzeug.exceptions import PreconditionFailed, InternalServerError
from sqlalchemy import or_
from flask import g, request

from hackathon.database import Hackathon, User, UserHackathonRel, AdminHackathonRel, DockerHostServer, Template
from hackathon.hackathon_response import internal_server_error, bad_request, ok
from hackathon.constants import HACKATHON_BASIC_INFO, ADMIN_ROLE_TYPE, HACK_STATUS, RGStatus, VE_PROVIDER, HTTP_HEADER, \
    FILE_TYPE, HACK_TYPE
from hackathon import RequiredFeature, Component, Context

__all__ = ["HackathonManager"]


class HackathonManager(Component):
    """Component to manage hackathon

    Note that it only handle operations directly related to Hackathon table. Things like registerd users, templates are
    in separated components
    """

    BASIC_INFO = 'basic_info'
    EXTRA_INFO = 'extra_info'

    admin_manager = RequiredFeature("admin_manager")

    def get_hackathon_by_name_or_id(self, hack_id=None, name=None):
        if hack_id is None:
            return self.__get_hackathon_by_name(name)
        return self.get_hackathon_by_id(hack_id)

    def get_hackathon_by_id(self, hackathon_id):
        """Query hackathon by id

        :return hackathon instance or None
        """
        return self.db.find_first_object_by(Hackathon, id=hackathon_id)

    def get_hackathon_stat(self, hackathon):
        reg_list = hackathon.registers.filter(UserHackathonRel.deleted != 1,
                                              UserHackathonRel.status.in_([RGStatus.AUTO_PASSED,
                                                                           RGStatus.AUDIT_PASSED])).all()

        reg_count = len(reg_list)
        stat = {
            "total": reg_count,
            "hid": hackathon.id,
            "online": 0,
            "offline": reg_count
        }

        if reg_count > 0:
            user_id_list = [r.user_id for r in reg_list]
            user_id_online = self.db.count(User, (User.id.in_(user_id_list) & (User.online == 1)))
            stat["online"] = user_id_online
            stat["offline"] = reg_count - user_id_online

        return stat

    def get_hackathon_list(self, user_id=None, status=None):
        status_cond = Hackathon.status == status if status is not None else Hackathon.status > -1
        user_cond = or_(UserHackathonRel.user_id == user_id, UserHackathonRel.user_id == None)

        if user_id is None:
            return [r.dic() for r in self.db.find_all_objects(Hackathon, status_cond)]

        hackathon_with_user_list = self.db.session().query(Hackathon, UserHackathonRel). \
            outerjoin(UserHackathonRel, UserHackathonRel.user_id == user_id) \
            .filter(UserHackathonRel.deleted != 1, status_cond, user_cond) \
            .all()

        def to_dict(hackathon, register):
            dic = hackathon.dic()
            if register is not None:
                dic["registration"] = register.dic()

            return dic

        return map(lambda (hack, reg): to_dict(hack, reg), hackathon_with_user_list)

    def is_hackathon_name_existed(self, name):
        """Check whether hackathon with specific name exists or not

        :type name: str|unicode
        :param name: name of hackathon

        :rtype: bool
        :return True if hackathon with specific name exists otherwise False
        """
        hackathon = self.__get_hackathon_by_name(name)
        return hackathon is not None

    def get_online_hackathons(self):
        return self.db.find_all_objects(Hackathon, Hackathon.status == HACK_STATUS.ONLINE)

    def get_user_hackathon_list(self, user_id):
        user_hack_list = self.db.session().query(Hackathon, UserHackathonRel) \
            .outerjoin(UserHackathonRel, UserHackathonRel.user_id == user_id) \
            .filter(UserHackathonRel.deleted != 1, UserHackathonRel.user_id == user_id).all()

        return [h.dic() for h in user_hack_list]

    def get_entitled_hackathon_list(self, user_id):
        hackathon_ids = self.admin_manager.get_entitled_hackathon_ids(user_id)
        if -1 in hackathon_ids:
            hackathon_list = self.db.find_all_objects(Hackathon)
        else:
            hackathon_list = self.db.find_all_objects(Hackathon, Hackathon.id.in_(hackathon_ids))

        return map(lambda u: u.dic(), hackathon_list)

    def get_basic_property(self, hackathon, key, default=None):
        """Get basic property of hackathon from hackathon.basic_info"""
        try:
            basic_info = json.loads(hackathon.basic_info)
            return basic_info.get(key, default)
        except Exception as e:
            self.log.error(e)
            self.log.warn(
                "cannot get %s from basic info for hackathon %d, will return default value" % (key, hackathon.id))
            return default

    def validate_hackathon_name(self):
        if HTTP_HEADER.HACKATHON_NAME in request.headers:
            try:
                hackathon_name = request.headers[HTTP_HEADER.HACKATHON_NAME]
                hackathon = self.__get_hackathon_by_name(hackathon_name)
                if hackathon is None:
                    self.log.debug("cannot find hackathon by name %s" % hackathon_name)
                    return False
                else:
                    g.hackathon = hackathon
                    return True
            except Exception as ex:
                self.log.error(ex)
                self.log.debug("hackathon_name invalid")
                return False
        else:
            self.log.debug("hackathon_name not found in headers")
            return False

    def is_recycle_enabled(self, hackathon):
        key = HACKATHON_BASIC_INFO.RECYCLE_ENABLED
        return self.get_basic_property(hackathon, key, False)

    def get_recycle_minutes(self, hackathon):
        key = HACKATHON_BASIC_INFO.RECYCLE_MINUTES
        return self.get_basic_property(hackathon, key, 60)

    def create_new_hackathon(self, context):
        """Create new hackathon based on the http body

        Hackathon name is unique so duplicated names are not allowd.

        :type context: Context
        :param context: the body of http request that contains fields to create a new hackathon

        :rtype: dict
        """
        hackathon = self.__get_hackathon_by_name(context.name)
        if hackathon is not None:
            raise PreconditionFailed("hackathon name already exists")

        self.log.debug("add a new hackathon:" + repr(context))
        new_hack = self.__create_hackathon(context)

        # todo remove the following line ASAP
        self.__test_data(new_hack)

        return new_hack.dic()

    def update_hackathon(self, args):
        """Update hackathon properties

        :type args: dict
        :param args: arguments from http request body that contains properties with new values

        :rtype dict
        :return hackathon in dict if updated successfully.
        """
        self.log.debug("update a exist hackathon insert args: %r" % args)
        hackathon = g.hackathon

        try:
            update_items = self.__parse_update_items(args, hackathon)
            self.log.debug("update hackathon items :" + str(args))
            self.db.update_object(hackathon, **update_items)
            return hackathon.dic()
        except Exception as e:
            self.log.error(e)
            return internal_server_error("fail to update hackathon")

    def validate_args(self):
        # check size
        if request.content_length > len(request.files) * self.util.get_config("storage.size_limit_kilo_bytes") * 1024:
            return False, bad_request("more than the file size limited")

        # check each file type
        for file_name in request.files:
            if request.files.get(file_name).filename.endswith('jpg'): continue  # jpg is not considered in imghdr
            if imghdr.what(request.files.get(file_name)) is None:
                return False, bad_request("only images can be uploaded")

        return True, "passed"

    def generate_file_name(self, file):
        # refresh file_name = hack_name + uuid(10) + time + suffix
        suffix = file.filename.split('.')[-1]
        real_name = g.hackathon.name + "/" + \
                    str(uuid.uuid1())[0:9] + \
                    time.strftime("%Y%m%d%H%M%S") + "." + suffix
        return real_name

    def upload_files(self):
        status, return_info = self.validate_args()
        if not status:
            return return_info

        image_container_name = self.util.safe_get_config("storage.image_container", "images")
        images = []
        storage = RequiredFeature("storage")
        for file_name in request.files:
            file = request.files[file_name]
            self.log.debug("upload image file : " + file_name)
            context = Context(
                hackathon_name=g.hackathon.name,
                file_name=file.filename,
                file_type=FILE_TYPE.HACK_IMAGE,
                content=file
            )
            context = storage.save(context)
            image = {}
            image['name'] = file.filename
            image['url'] = context.url
            image['thumbnailUrl'] = context.url
            # context.file_name is a random name created by server, file.filename is the original name
            image['deleteUrl'] = '/api/admin/file?key=' + context.file_name
            images.append(image)

        return {"files": images}

    def get_recyclable_hackathon_list(self):
        all = self.db.find_all_objects(Hackathon)
        return filter(lambda h: self.is_recycle_enabled(h), all)

    def get_pre_allocate_enabled_hackathon_list(self):
        # only online hackathons will be in consideration
        online = self.get_online_hackathons()
        pre_list = filter(lambda hackathon: hackathon.is_pre_allocate_enabled(), online)
        return [h.id for h in pre_list]

    # ---------------------------- private methods ---------------------------------------------------

    def __get_default_basic_info(self):
        """Return the default basic info of hackathon"""
        default_base_info = {
            HACKATHON_BASIC_INFO.ORGANIZERS: [],
            # HACKATHON_BASIC_INFO.ORGANIZER_NAME: "",
            # HACKATHON_BASIC_INFO.ORGANIZER_URL: "",
            # HACKATHON_BASIC_INFO.ORGANIZER_IMAGE: "",
            # HACKATHON_BASIC_INFO.ORGANIZER_DESCRIPTION: "",
            HACKATHON_BASIC_INFO.BANNERS: "",
            HACKATHON_BASIC_INFO.LOCATION: "",
            HACKATHON_BASIC_INFO.MAX_ENROLLMENT: 0,
            HACKATHON_BASIC_INFO.WALL_TIME: time.strftime("%Y-%m-%d %H:%M:%S"),
            HACKATHON_BASIC_INFO.AUTO_APPROVE: False,
            HACKATHON_BASIC_INFO.RECYCLE_ENABLED: False,
            HACKATHON_BASIC_INFO.RECYCLE_MINUTES: 0,
            HACKATHON_BASIC_INFO.PRE_ALLOCATE_ENABLED: False,
            HACKATHON_BASIC_INFO.PRE_ALLOCATE_NUMBER: 1,
            HACKATHON_BASIC_INFO.ALAUDA_ENABLED: False,
            HACKATHON_BASIC_INFO.FREEDOM_TEAM: True
        }
        return json.dumps(default_base_info)

    def __get_hackathon_by_name(self, name):
        """Get hackathon accoring the unique name

        :type name: str|unicode
        :param name: name of hackathon

        :rtype: Hackathon
        :return hackathon instance if found else None
        """
        return self.db.find_first_object_by(Hackathon, name=name)

    def __create_hackathon(self, context):
        """Insert hackathon and admin_hackathon_rel to database

        We enforce that default basic_info are used during the creation

        :type context: Context
        :param context: context of the args to create a new hackathon

        :rtype: Hackathon
        :return hackathon instance
        """

        new_hack = Hackathon(
            name=context.name,
            display_name=context.display_name,
            description=context.get("description"),
            status=HACK_STATUS.INIT,
            creator_id=g.user.id,
            event_start_time=context.get("event_start_time"),
            event_end_time=context.get("event_end_time"),
            registration_start_time=context.get("registration_start_time"),
            registration_end_time=context.get("registration_end_time"),
            judge_start_time=context.get("judge_start_time"),
            judge_end_time=context.get("judge_end_time"),
            basic_info=self.__get_default_basic_info(),
            extra_info=context.get("extra_info"),
            type=context.get("type", HACK_TYPE.HACKATHON)
        )

        # insert into table hackathon
        self.db.add_object(new_hack)

        # add the current login user as admin and creator
        try:
            ahl = AdminHackathonRel(user_id=g.user.id,
                                    role_type=ADMIN_ROLE_TYPE.ADMIN,
                                    hackathon_id=new_hack.id,
                                    status=HACK_STATUS.INIT,
                                    remarks='creator',
                                    create_time=self.util.get_now())
            self.db.add_object(ahl)
        except Exception as ex:
            # TODO: send out a email to remind administrator to deal with this problems
            self.log.error(ex)
            raise InternalServerError("fail to create the default administrator")

        return new_hack

    def __parse_update_items(self, args, hackathon):
        """Parse properties that need to update

        Only those whose value changed items will be returned. Also some static property like id, create_time should
        NOT be updated.

        :type args: dict
        :param args: arguments from http body which contains new values

        :type hackathon: Hackathon
        :param hackathon: the existing Hackathon object which contains old values

        :rtype: dict
        :return a dict that contains all properties that are updated.
        """
        result = {}

        for key in dict(args):
            if key == self.BASIC_INFO:
                result[self.BASIC_INFO] = json.dumps(args[self.BASIC_INFO])
            elif key == self.EXTRA_INFO:
                result[self.EXTRA_INFO] = json.dumps(args[self.EXTRA_INFO])
            elif dict(args)[key] != hackathon.dic()[key]:
                result[key] = dict(args)[key]

        result.pop('id', None)
        result.pop('create_time', None)
        result.pop('creator_id', None)
        result['update_time'] = self.util.get_now()
        return result

    def __test_data(self, hackathon):
        """
        create test data for new hackathon. Remove this function after template and docker host feature done
        :param hackathon:
        :return:
        """
        try:
            # test docker host server
            docker_host = DockerHostServer(vm_name="OSSLAB-VM-19", public_dns="osslab-vm-19.chinacloudapp.cn",
                                           public_ip="42.159.97.143", public_docker_api_port=4243,
                                           private_ip="10.209.14.33",
                                           private_docker_api_port=4243, container_count=0, container_max_count=100,
                                           hackathon=hackathon)
            if self.db.find_first_object_by(DockerHostServer, vm_name=docker_host.vm_name,
                                            hackathon_id=hackathon.id) is None:
                self.db.add_object(docker_host)
        except Exception as e:
            self.log.error(e)
            self.log.warn("fail to create test data")

        return


'''
Attach extension methods to Hackathon entity so that we can code like 'if hackathon.is_auto_approve(): ....' where
hackathon is entity of Hackathon that defines in database/models.py.
'''


def is_auto_approve(hackathon):
    hack_manager = RequiredFeature("hackathon_manager")
    value = hack_manager.get_basic_property(hackathon, HACKATHON_BASIC_INFO.AUTO_APPROVE, 1)
    return value == 1


def is_pre_allocate_enabled(hackathon):
    hack_manager = RequiredFeature("hackathon_manager")
    value = hack_manager.get_basic_property(hackathon, HACKATHON_BASIC_INFO.PRE_ALLOCATE_ENABLED, 1)
    return value == 1


def get_pre_allocate_number(hackathon):
    hack_manager = RequiredFeature("hackathon_manager")
    return hack_manager.get_basic_property(hackathon, HACKATHON_BASIC_INFO.PRE_ALLOCATE_NUMBER, 1)


def is_alauda_enabled(hackathon):
    hack_manager = RequiredFeature("hackathon_manager")
    return hack_manager.get_basic_property(hackathon, HACKATHON_BASIC_INFO.ALAUDA_ENABLED, False)


def get_basic_property(hackathon, property_name, default_value=None):
    hack_manager = RequiredFeature("hackathon_manager")
    return hack_manager.get_basic_property(hackathon, property_name, default_value)


Hackathon.is_auto_approve = is_auto_approve
Hackathon.is_pre_allocate_enabled = is_pre_allocate_enabled
Hackathon.get_pre_allocate_number = get_pre_allocate_number
Hackathon.is_alauda_enabled = is_alauda_enabled
Hackathon.get_basic_property = get_basic_property
