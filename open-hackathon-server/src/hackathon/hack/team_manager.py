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

from hackathon import Component, RequiredFeature
from hackathon.database import Team, AdminHackathonRel, User

__all__ = ["TeamManager"]


class TeamManager(Component):
    """Component to manage hackathon teams"""
    user_manager = RequiredFeature("user_manager")
    admin_manager = RequiredFeature("admin_manager")

    # ------------------------------ private methods ----------------------------------------
    def __init__(self):
        pass

    def __validate_team_permission(self, hackathon_id, team_name, user):
        """Validate current login user whether has proper right on specific team.

        :type hackathon_id: int
        :param hackathon_id: id of hackathon related to the team

        :type team_name: str | unicode
        :param team_name: name of the team

        :type user: User
        :param user: current login user

        :rtype: bool
        :return True if user is team leader, hackathon admin or super admin. Otherwise return False
        """
        # check if team leader
        if self.db.find_first_object_by(Team, hackathon_id=hackathon_id, name=team_name, leader_id=user.id):
            return True
        # check if hackathon admin
        elif self.admin_manager.is_hackathon_admin(hackathon_id, user):
            return True
        # check if super admin
        return self.user_manager.is_super_admin(user)
