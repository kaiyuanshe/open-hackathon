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
from hackathon.database.models import Hackathon, User, UserHackathonRel, AdminHackathonRel, DockerHostServer, Template
from hackathon.enum import RGStatus, VEProvider
from hackathon.hackathon_response import internal_server_error, bad_request, ok
from hackathon.enum import ADMIN_ROLE_TYPE, HACK_STATUS
from sqlalchemy import or_
from hackathon.constants import HTTP_HEADER
import json
from hackathon.constants import HACKATHON_BASIC_INFO
from hackathon import RequiredFeature, Component
from flask import g, request
import imghdr
import uuid
import time
import os
from os.path import realpath, dirname


class HackathonManager(Component):
    BASIC_INFO = 'basic_info'
    EXTRA_INFO = 'extra_info'
    file_service = RequiredFeature("file_service")

    def __is_recycle_enabled(self, hackathon):
        key = HACKATHON_BASIC_INFO.RECYCLE_ENABLED
        value = self.__get_property_from_hackathon_basic_info(hackathon, key)
        return value == 1

    # check the admin authority on hackathon
    def validate_admin_privilege(self, user_id, hackathon_id):
        hack_ids = self.__get_hackathon_ids_by_admin_user_id(user_id)
        return -1 in hack_ids or hackathon_id in hack_ids

    def get_hackathon_by_name_or_id(self, hack_id=None, name=None):
        if hack_id is None:
            return self.get_hackathon_by_name(name)
        return self.get_hackathon_by_id(hack_id)

    def get_hackathon_by_name(self, name):
        return self.db.find_first_object_by(Hackathon, name=name)

    def get_hackathon_by_id(self, hackathon_id):
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

    def get_online_hackathons(self):
        return self.db.find_all_objects(Hackathon, Hackathon.status == HACK_STATUS.ONLINE)

    def get_user_hackathon_list(self, user_id):
        user_hack_list = self.db.session().query(Hackathon, UserHackathonRel) \
            .outerjoin(UserHackathonRel, UserHackathonRel.user_id == user_id) \
            .filter(UserHackathonRel.deleted != 1, UserHackathonRel.user_id == user_id).all()

        return [h.dic() for h in user_hack_list]

    def get_permitted_hackathon_list_by_admin_user_id(self, user_id):
        hackathon_ids = self.__get_hackathon_ids_by_admin_user_id(user_id)
        if -1 in hackathon_ids:
            hackathon_list = self.db.find_all_objects(Hackathon)
        else:
            hackathon_list = self.db.find_all_objects(Hackathon, Hackathon.id.in_(hackathon_ids))

        return map(lambda u: u.dic(), hackathon_list)

    def __get_hackathon_ids_by_admin_user_id(self, user_id):
        # get AdminUserHackathonRels from query withn filter by email
        admin_user_hackathon_rels = self.db.find_all_objects_by(AdminHackathonRel, user_id=user_id)

        # get hackathon_ids_from AdminUserHackathonRels details
        hackathon_ids = map(lambda x: x.hackathon_id, admin_user_hackathon_rels)

        return list(set(hackathon_ids))

    def __get_property_from_hackathon_basic_info(self, hackathon, key):
        try:
            basic_info = json.loads(hackathon.basic_info)
            value = basic_info[key]
            return value
        except Exception as e:
            self.log.error(e)
            self.log.warn("cannot get %s from basic info for hackathon %d, will return None" % (key, hackathon.id))
            return None

    def validate_admin_privilege_http(self):
        return self.validate_admin_privilege(g.user.id, g.hackathon.id)

    def validate_hackathon_name(self):
        if HTTP_HEADER.HACKATHON_NAME in request.headers:
            try:
                hackathon_name = request.headers[HTTP_HEADER.HACKATHON_NAME]
                hackathon = self.get_hackathon_by_name(hackathon_name)
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

    def is_auto_approve(self, hackathon):
        key = HACKATHON_BASIC_INFO.AUTO_APPROVE
        value = self.__get_property_from_hackathon_basic_info(hackathon, key)
        return value == 1

    def is_pre_allocate_enabled(self, hackathon):
        try:
            basic_info = json.loads(hackathon.basic_info)
            k = HACKATHON_BASIC_INFO.PRE_ALLOCATE_ENABLED
            return k in basic_info and basic_info[k] == 1
        except Exception as e:
            self.log.error(e)
            self.log.warn(
                "cannot load pre_allocate_enabled from basic info for hackathon %d, will return False" % hackathon.id)
            return False


    def is_alauda_enabled(self, hackathon):
        key = HACKATHON_BASIC_INFO.ALAUDA_ENABLED
        value = self.__get_property_from_hackathon_basic_info(hackathon, key)
        return value if value is not None else False

    def get_pre_allocate_number(self, hackathon):
        key = HACKATHON_BASIC_INFO.PRE_ALLOCATE_NUMBER
        value = self.__get_property_from_hackathon_basic_info(hackathon, key)
        return value if value is not None else 1

    def validate_created_args(self, args):
        self.log.debug("create_or_update_hackathon: %r" % args)
        if "name" not in args:
            return False, bad_request("hackathon name invalid")

        hackathon = self.get_hackathon_by_name(args['name'])
        if hackathon is not None:
            return False, internal_server_error("hackathon name already exist")

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
            HACKATHON_BASIC_INFO.PRE_ALLOCATE_ENABLED: False,
            HACKATHON_BASIC_INFO.PRE_ALLOCATE_NUMBER: 1,
            HACKATHON_BASIC_INFO.ALAUDA_ENABLED: False
        }
        args[self.BASIC_INFO] = json.dumps(default_base_info)
        return True, args

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

            # test template: ubuntu terminal
            template_dir = dirname(dirname(realpath(__file__))) + '/resources'
            template_url = template_dir + os.path.sep + "kaiyuanshe-ut.js"
            template = Template(name="ut", url=template_url,
                                provider=VEProvider.Docker,
                                status=1,
                                virtual_environment_count=1,
                                description="<ul><li>Ubuntu</li><li>SSH</li><li>LAMP</li></ul>",
                                hackathon=hackathon)
            if self.db.find_first_object_by(Template, name=template.name, hackathon_id=hackathon.id) is None:
                self.db.add_object(template)
        except:
            self.log.warn("fail to create test data")

        return

    def create_new_hackathon(self, args):
        status, return_info = self.validate_created_args(args)
        if not status:
            return return_info
        args = return_info

        try:
            self.log.debug("add a new hackathon:" + str(args))
            args['update_time'] = self.util.get_now()
            args['create_time'] = self.util.get_now()
            args["creator_id"] = g.user.id
            new_hack = self.db.add_object_kwargs(Hackathon, **args)  # insert into hackathon
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
                return internal_server_error("fail to insert a record into admin_hackathon_rel")

            # todo remove the following line ASAP
            self.__test_data(new_hack)
            return new_hack.id
        except Exception as  e:
            self.log.error(e)
            return internal_server_error("fail to create hackathon")


    def update_hackathon(self, args):
        self.log.debug("update a exist hackathon insert args: %r" % args)
        if "name" not in args or "id" not in args:
            return bad_request("name or id are both required when update a hackathon")

        hackathon = self.db.find_first_object(Hackathon, Hackathon.name == args['name'])

        if hackathon.id != args['id']:
            return bad_request("name and id are not matched in hackathon")

        try:
            update_items = self.parse_update_items(args, hackathon)
            self.log.debug("update hackathon items :" + str(args))
            self.db.update_object(hackathon, **update_items)
            return ok("update hackathon succeed")

        except Exception as  e:
            self.log.error(e)
            return internal_server_error("fail to update hackathon")


    def parse_update_items(self, args, hackathon):
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
        suffix = file.filename.split('.')[1]
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

        for file_name in request.files:
            file = request.files[file_name]
            real_name = self.generate_file_name(file)
            self.log.debug("upload image file : " + real_name)

            url = self.file_service.upload_file_to_azure(file, image_container_name, real_name)
            if url is not None:
                image = {}
                image['name'] = file.filename
                image['url'] = url
                # frontUI components needed return values
                image['thumbnailUrl'] = url
                image['deleteUrl'] = '/api/file?key=' + real_name
                images.append(image)
            else:
                return internal_server_error("upload file failed")

        return {"files": images}


    def get_recyclable_hackathon_list(self):
        all = self.db.find_all_objects(Hackathon)
        recyclable = filter(lambda h: self.__is_recycle_enabled(h), all)
        return [h.id for h in recyclable]


    def get_pre_allocate_enabled_hackathon_list(self):
        # only online hackathons will be in consideration
        all = self.get_online_hackathons()
        pre_list = filter(lambda h: self.is_pre_allocate_enabled(h), all)
        return [h.id for h in pre_list]


def is_auto_approve(hackathon):
    hack_manager = RequiredFeature("hackathon_manager")
    return hack_manager.is_auto_approve(hackathon)


def is_pre_allocate_enabled(hackathon):
    hack_manager = RequiredFeature("hackathon_manager")
    return hack_manager.is_pre_allocate_enabled(hackathon)


def get_pre_allocate_number(hackathon):
    hack_manager = RequiredFeature("hackathon_manager")
    return hack_manager.get_pre_allocate_number(hackathon)


def is_alauda_enabled(hackathon):
    hack_manager = RequiredFeature("hackathon_manager")
    return hack_manager.is_alauda_enabled(hackathon)


Hackathon.is_auto_approve = is_auto_approve
Hackathon.is_pre_allocate_enabled = is_pre_allocate_enabled
Hackathon.get_pre_allocate_number = get_pre_allocate_number
Hackathon.is_alauda_enabled = is_alauda_enabled
