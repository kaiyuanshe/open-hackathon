# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")


class User():
    def __init__(self, dic):
        for key, value in dic.iteritems():
            setattr(self, key, value)

    def get_avatar_url(self):
        ret = None
        if hasattr(self, "profile"):
            ret = self.profile.get("avatar_url", None)

        if not ret and hasattr(self, "avatar_url"):
            ret = self.avatar_url

        return ret

    def get_user_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.get_user_id())

    def is_super(self):
        return self.is_super

    def __repr__(self):
        return repr(self.__dict__)
