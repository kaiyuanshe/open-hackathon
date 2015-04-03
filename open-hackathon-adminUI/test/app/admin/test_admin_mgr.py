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

sys.path.append("../src/")
import unittest
from app.admin.admin_mgr import AdminManager
from app.database.models import AdminUser, AdminEmail, AdminUserHackathonRel
from hackathon import app
from mock import Mock, ANY
from flask import g


class AdminManagerTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        pass

    '''test method: get_hackid_from_adminid'''

    def test_get_hackid_by_adminid(self):
        admin_email_test = [AdminEmail(email='test@ms.com')]
        admin_user_hackathon_rel = [AdminUserHackathonRel(hackathon_id=-1)]

        mock_db = Mock()
        mock_db.find_all_objects_by.return_value = admin_email_test
        mock_db.find_all_objects.return_value = admin_user_hackathon_rel

        am = AdminManager(mock_db)

        self.assertEqual(am.get_hackid_from_adminid(1), [-1L])
        mock_db.find_all_objects_by.assert_called_once_with(AdminEmail, admin_id=1)
        mock_db.find_all_objects.assert_called_once_with(AdminUserHackathonRel, ANY)


    '''test method: check_role for decorators'''

    def test_check_role_super_admin_success(self):
        admin_email_test = [AdminEmail(email='test@ms.com')]
        admin_user_hackathon_rel = [AdminUserHackathonRel(hackathon_id=-1)]

        mock_db = Mock()
        mock_db.find_all_objects_by.return_value = admin_email_test
        mock_db.find_all_objects.return_value = admin_user_hackathon_rel

        am = AdminManager(mock_db)
        with app.test_request_context('/'):
            g.admin = AdminUser(id=1, name='testadmin')
            self.assertTrue(am.check_role(0))
            mock_db.find_all_objects_by.assert_called_once_with(AdminEmail, admin_id=1)
            mock_db.find_all_objects.assert_called_once_with(AdminUserHackathonRel, ANY)

    def test_check_role_super_admin_faild(self):
        admin_email_test = [AdminEmail(email='test@ms.com')]
        admin_user_hackathon_rel = [AdminUserHackathonRel(hackathon_id=2)]

        mock_db = Mock()
        mock_db.find_all_objects_by.return_value = admin_email_test
        mock_db.find_all_objects.return_value = admin_user_hackathon_rel

        am = AdminManager(mock_db)
        with app.test_request_context('/'):
            g.admin = AdminUser(id=1, name='testadmin')
            self.assertFalse(am.check_role(0))
            mock_db.find_all_objects_by.assert_called_once_with(AdminEmail, admin_id=1)
            mock_db.find_all_objects.assert_called_once_with(AdminUserHackathonRel, ANY)

    def test_check_role_common_admin_success(self):
        admin_email_test = [AdminEmail(email='test@ms.com')]
        admin_user_hackathon_rel = [AdminUserHackathonRel(hackathon_id=2)]

        mock_db = Mock()
        mock_db.find_all_objects_by.return_value = admin_email_test
        mock_db.find_all_objects.return_value = admin_user_hackathon_rel

        am = AdminManager(mock_db)
        with app.test_request_context('/'):
            g.admin = AdminUser(id=1, name='testadmin')
            self.assertTrue(am.check_role(1))
            mock_db.find_all_objects_by.assert_called_once_with(AdminEmail, admin_id=1)
            mock_db.find_all_objects.assert_called_once_with(AdminUserHackathonRel, ANY)

    def test_check_role_common_admin_faild(self):
        admin_email_test = [AdminEmail(email='test@ms.com')]
        admin_user_hackathon_rel = None

        mock_db = Mock()
        mock_db.find_all_objects_by.return_value = admin_email_test
        mock_db.find_all_objects.return_value = admin_user_hackathon_rel

        am = AdminManager(mock_db)
        with app.test_request_context('/'):
            g.admin = AdminUser(id=1, name='testadmin')
            self.assertFalse(am.check_role(1))
            mock_db.find_all_objects_by.assert_called_once_with(AdminEmail, admin_id=1)
