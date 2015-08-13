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
import time

from flask import g, request

from hackathon import RequiredFeature
from hackathon.decorators import hackathon_name_required, token_required, admin_privilege_required
from hackathon.health import report_health
from hackathon.hackathon_response import not_found
from hackathon_resource import Resource, HackathonResource

hackathon_manager = RequiredFeature("hackathon_manager")
user_manager = RequiredFeature("user_manager")
register_manager = RequiredFeature("register_manager")
template_manager = RequiredFeature("template_manager")
team_manager = RequiredFeature("team_manager")


class HealthResource(HackathonResource):
    def get(self):
        context = self.context()
        return report_health(context.get("q"))


class CurrentTimeResource(HackathonResource):
    def get(self):
        return {
            "currenttime": long(time.time() * 1000)
        }


class AdminHackathonResource(HackathonResource):
    """Resource for admin to create/update hackathon

    url path: /api/admin/hackathon
    """

    @hackathon_name_required
    def get(self):
        return g.hackathon.dic()

    @token_required
    def post(self):
        return hackathon_manager.create_new_hackathon(self.context())

    @admin_privilege_required
    def put(self):
        return hackathon_manager.update_hackathon(request.get_json())


class HackathonCheckNameResource(HackathonResource):
    def get(self):
        context = self.context()
        return hackathon_manager.is_hackathon_name_existed(context.name)
