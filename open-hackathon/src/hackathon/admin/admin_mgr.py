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
from hackathon.constants import HTTP_HEADER
from flask import request, g
from hackathon.log import log


class AdminManager(object):
    def __init__(self, db_adapter):
        self.db = db_adapter

    def get_hack_id_by_user_id(self, user_id):

        # get AdminUserHackathonRels from query withn filter by email
        admin_user_hackathon_rels = self.db.find_all_objects_by(AdminHackathonRel, user_id=user_id)

        # get hackathon_ids_from AdminUserHackathonRels details
        hackathon_ids = map(lambda x: x.hackathon_id, admin_user_hackathon_rels)

        return list(set(hackathon_ids))


    # check the admin authority on hackathon
    def validate_admin_hackathon_request(self, hackathon_id):
        if HTTP_HEADER.TOKEN not in request.headers:
            return True

        hack_ids = self.get_hack_id_by_user_id(g.user.id)
        return -1 in hack_ids or hackathon_id in hack_ids


    def validate_hackathon_id(self):
        if HTTP_HEADER.HACKATHON_ID in request.headers:
            try:
                g.hackathon_id = long(request.headers[HTTP_HEADER.HACKATHON_ID])
                return self.validate_admin_hackathon_request(g.hackathon_id)
            except Exception:
                log.debug("hackathon_id is not a num")
                return False
        else:
            log.debug("HEARDER lost hackathon_id")
            return False


admin_manager = AdminManager(db_adapter)

