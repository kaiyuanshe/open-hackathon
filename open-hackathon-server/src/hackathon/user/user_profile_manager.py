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

from flask import g

from hackathon.hmongo.models import User, UserProfile
from hackathon.hackathon_response import internal_server_error
from hackathon import Component

__all__ = ["UserProfileManager"]


class UserProfileManager(Component):
    """Component to manager user profile"""

    def get_user_profile(self, user_id):
        return User.objects.get(id=user_id).profile

    def create_user_profile(self, args):
        self.log.debug("create_user_profile: %r" % args)
        try:
            u_id = g.user.id
            user = User.objects.get(id=u_id)
            user.profile = UserProfile(**args)
            user.save()
            return user.dic()
        except Exception as e:
            self.log.debug(e)
            return internal_server_error("failed to create user profile")

    def update_user_profile(self, args):
        self.log.debug("update_user_profile")
        try:
            u_id = args["user_id"]
            user = User.objects.get(id=u_id)
            user.profile = UserProfile(**args)
            user.save()
            return user.dic()
        except Exception as e:
            self.log.debug(e)
            return internal_server_error("failed to update user profile")
