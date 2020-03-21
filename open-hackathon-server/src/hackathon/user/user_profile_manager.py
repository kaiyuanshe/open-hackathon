# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")

from flask import g

from hackathon.hmongo.models import User, UserProfile
from hackathon.hackathon_response import internal_server_error, not_found
from hackathon import Component

__all__ = ["UserProfileManager"]


class UserProfileManager(Component):
    """Component to manager user profile"""

    def get_user_profile(self, user_id):
        user = User.objects.get(id=user_id)
        if not user:
            return not_found("user {} not found".format(user_id))
        profile = User.objects.get(id=user_id).profile
        if profile:
            return user.dic()
        # if user do not create profile, create default
        user.profile = UserProfile()
        user.save()
        return user.dic()

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
