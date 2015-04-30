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
from hackathon.database.models import Hackathon, User, UserHackathonRel, AdminHackathonRel
from hackathon.database import db_adapter
from hackathon.database import db_session
from datetime import datetime
from hackathon.enum import RGStatus
from hackathon.hackathon_response import *
from hackathon.enum import ADMIN_ROLE_TYPE
from sqlalchemy import or_
from hackathon.constants import HTTP_HEADER
from flask import request, g
import json
from hackathon.constants import HACKATHON_BASIC_INFO


class HackathonManager():
    def __init__(self, db):
        self.db = db

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

        hackathon_with_user_list = self.db.session.query(Hackathon, UserHackathonRel). \
            outerjoin(UserHackathonRel, UserHackathonRel.user_id == user_id) \
            .filter(UserHackathonRel.deleted != 1, status_cond, user_cond) \
            .all()

        def to_dict(hackathon, register):
            dic = hackathon.dic()
            if register is not None:
                dic["registration"] = register.dic()

            return dic

        return map(lambda (hack, reg): to_dict(hack, reg), hackathon_with_user_list)


    def get_user_hackathon_list(self, user_id):
        user_hack_list = self.db.session.query(Hackathon, UserHackathonRel) \
            .outerjoin(UserHackathonRel, UserHackathonRel.user_id == user_id) \
            .filter(UserHackathonRel.deleted != 1, UserHackathonRel.user_id == user_id).all()

        return [h.dic() for h in user_hack_list]

    def get_user_hackathon_detail(self, user_id, hackathon):
        user_hackathon = self.db.find_first_object_by(UserHackathonRel,
                                                      user_id=user_id,
                                                      hackathon_id=hackathon.id,
                                                      deleted=0)

        if user_hackathon is None:
            return not_found("")
        return ""

    def get_permitted_hackathon_list_by_admin_user_id(self, user_id):
        # get AdminUserHackathonRels from query withn filter by email
        admin_user_hackathon_rels = self.db.find_all_objects_by(AdminHackathonRel, user_id=user_id)

        # get hackathon_ids_from AdminUserHackathonRels details
        hackathon_ids = map(lambda x: x.hackathon_id, admin_user_hackathon_rels)

        return list(set(hackathon_ids))


    # check the admin authority on hackathon
    def __validate_admin_privilege(self, user_id, hackathon_id):
        hack_ids = self.get_permitted_hackathon_list_by_admin_user_id(user_id)
        return -1 in hack_ids or hackathon_id in hack_ids

    def validate_admin_privilege(self):
        return self.__validate_admin_privilege(g.user.id, g.hackathon.id)

    def validate_hackathon_name(self):
        if HTTP_HEADER.HACKATHON_NAME in request.headers:
            try:
                hackathon_name = request.headers[HTTP_HEADER.HACKATHON_NAME]
                hackathon = hack_manager.get_hackathon_by_name(hackathon_name)
                if hackathon is None:
                    log.debug("cannot find hackathon by name %s" % hackathon_name)
                    return False
                else:
                    g.hackathon = hackathon
                    return True
            except Exception:
                log.debug("hackathon_name invalid")
                return False
        else:
            log.debug("hackathon_name not found in headers")
            return False

    def is_auto_approve(self, hackathon):
        try:
            basic_info = json.loads(hackathon.basic_info)
            return basic_info[HACKATHON_BASIC_INFO.AUTO_APPROVE] == 1
        except Exception as e:
            log.error(e)
            log.warn("cannot load auto_approve from basic info for hackathon %d, will return False" % hackathon.id)
            return False

    def is_recycle_enabled(self, hackathon):
        try:
            basic_info = json.loads(hackathon.basic_info)
            return basic_info[HACKATHON_BASIC_INFO.RECYCLE_ENABLED] == 1
        except Exception as e:
            log.error(e)
            log.warn("cannot load recycle_enabled from basic info for hackathon %d, will return False" % hackathon.id)
            return False

    def create_or_update_hackathon(self, args):
        log.debug("create_or_update_hackathon: %r" % args)
        if "name" not in args:
            return bad_request("hackathon perporities lost name")
        hackathon = self.db.find_first_object(Hackathon, Hackathon.name == args['name'])

        try:
            if hackathon is None:
                log.debug("add a new hackathon:" + str(args))

                hack_object = Hackathon(**args)
                db_session.add(hack_object)  # insert into hackathon
                hid = hack_object.id
                ahl = AdminHackathonRel(user_id=g.user_id,
                                        role_type=ADMIN_ROLE_TYPE.ADMIN,
                                        hackathon_id=hid,
                                        status=1,
                                        remarks='being admin automatically',
                                        create_time=datetime.utcnow())
                db_session.add(ahl)  # insert into AdminHackathonRel
                db_session.commit()
                return ok("create hackathon successed")
            else:
                args['update_time'] = datetime.utcnow()
                update_items = dict(dict(args).viewitems() - hackathon.dic().viewitems())
                log.debug("update a exist hackathon " + hackathon.id + ":" + str(args))
                self.db.update_object(Hackathon, **update_items)
                return ok("update hackathon successed")
        except Exception as  e:
            log.error(e)
            return internal_server_error("fail to create or update hackathon")


hack_manager = HackathonManager(db_adapter)


def is_auto_approve(hackathon):
    return hack_manager.is_auto_approve(hackathon)


def is_recycle_enabled(hackathon):
    return hack_manager.is_recycle_enabled(hackathon)


Hackathon.is_auto_approve = is_auto_approve

