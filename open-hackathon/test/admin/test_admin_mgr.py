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

sys.path.append("../src/hackathon")
import unittest
from hackathon.admin.admin_mgr import AdminManager, admin_manager
from hackathon.database.models import AdminUser, AdminToken, AdminEmail, AdminUserHackathonRel
from hackathon import app
from mock import Mock, ANY, patch
from datetime import datetime, timedelta
from flask import request, g


class AdminManagerTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        pass


    '''test method: validate_request'''

    def test_validate_request_if_token_missing(self):
        am = AdminManager(None)
        '''more args for app.text_request_context:
                 path='/', base_url=None, query_string=None,
                 method='GET', input_stream=None, content_type=None,
                 content_length=None, errors_stream=None, multithread=False,
                 multiprocess=False, run_once=False, headers=None, data=None,
                 environ_base=None, environ_overrides=None, charset='utf-8'
        '''
        with app.test_request_context('/', headers=None):
            self.assertFalse("token" in request.headers)
            self.assertFalse(am.validate_request())

    def test_validate_request_token_not_found(self):
        token_value = "token_value"

        mock_db = Mock()
        mock_db.find_first_object_by.return_value = None
        am = AdminManager(mock_db)

        with app.test_request_context('/api', headers={"token": token_value}):
            self.assertTrue("token" in request.headers)
            self.assertFalse(am.validate_request())
            mock_db.find_first_object_by.assert_called_once_with(AdminToken, token=token_value)

    def test_validate_request_token_expired(self):
        token_value = "token_value"
        token = AdminToken(token=token_value, admin=None, expire_date=get_now() - timedelta(seconds=30))

        mock_db = Mock()
        mock_db.find_first_object_by.return_value = token

        am = AdminManager(mock_db)

        with app.test_request_context('/', headers={"token": token_value}):
            self.assertTrue("token" in request.headers)
            self.assertFalse(am.validate_request())
            mock_db.find_first_object_by.assert_called_once_with(AdminToken, token=token_value)

    def test_validate_request_token_valid(self):
        token_value = "token_value"
        admin = AdminUser(name="test_name")
        token = AdminToken(token=token_value, admin=admin, expire_date=get_now() + timedelta(seconds=30))

        mock_db = Mock()
        mock_db.find_first_object_by.return_value = token
        am = AdminManager(mock_db)

        with app.test_request_context('/', headers={"token": token_value}):
            self.assertTrue("token" in request.headers)
            self.assertTrue(am.validate_request())
            mock_db.find_first_object_by.assert_called_once_with(AdminToken, token=token_value)
            self.assertEqual(g.admin, admin)


    '''test method: get_hackid_from_adminid'''

    def test_get_hackid_by_adminid(self):
        admin_email_test = [AdminEmail(email='test@ms.com')]
        admin_user_hackathon_rel = [AdminUserHackathonRel(hackathon_id=-1)]

        mock_db = Mock()
        mock_db.find_all_objects_by.return_value = admin_email_test
        mock_db.find_all_objects.return_value = admin_user_hackathon_rel

        am = AdminManager(mock_db)

        self.assertEqual(am.get_hack_id_by_admin_id(1), [-1L])
        mock_db.find_all_objects_by.assert_called_once_with(AdminEmail, admin_id=1)
        mock_db.find_all_objects.assert_called_once_with(AdminUserHackathonRel, ANY)


    '''test method:validate_admin_hackathon_request'''

    def test_validate_admin_hackathon_request_token_missing(self):
        am = AdminManager(None)
        with app.test_request_context('/', headers=None):
            g.admin = AdminUser(id=1, name='testadmin')
            self.assertTrue(am.validate_admin_hackathon_request(1))
            self.assertFalse('token' in request.headers)

    def test_validate_admin_hackathon_request_super_admin(self):
        token_value = "token_value"
        admin_email_test = [AdminEmail(email='test@ms.com')]
        admin_user_hackathon_rel = [AdminUserHackathonRel(hackathon_id=-1L)]

        mock_db = Mock()
        mock_db.find_all_objects_by.return_value = admin_email_test
        mock_db.find_all_objects.return_value = admin_user_hackathon_rel

        am = AdminManager(mock_db)
        with app.test_request_context('/', headers={"token": token_value}):
            g.admin = AdminUser(id=1, name='testadmin')
            self.assertTrue(am.validate_admin_hackathon_request(1))
            mock_db.find_all_objects_by.assert_called_once_with(AdminEmail, admin_id=1)
            mock_db.find_all_objects.assert_called_once_with(AdminUserHackathonRel, ANY)

    def test_validate_admin_hackathon_request_have_authority(self):
        token_value = "token_value"
        admin_email_test = [AdminEmail(email='test@ms.com')]
        admin_user_hackathon_rel = [AdminUserHackathonRel(hackathon_id=1L)]

        mock_db = Mock()
        mock_db.find_all_objects_by.return_value = admin_email_test
        mock_db.find_all_objects.return_value = admin_user_hackathon_rel

        am = AdminManager(mock_db)
        with app.test_request_context('/', headers={"token": token_value}):
            g.admin = AdminUser(id=1, name='testadmin')
            self.assertTrue(am.validate_admin_hackathon_request(1))
            mock_db.find_all_objects_by.assert_called_once_with(AdminEmail, admin_id=1)
            mock_db.find_all_objects.assert_called_once_with(AdminUserHackathonRel, ANY)

    def test_validate_admin_hackathon_request_havnt_authority(self):
        token_value = "token_value"
        admin_email_test = [AdminEmail(email='test@ms.com')]
        admin_user_hackathon_rel = [AdminUserHackathonRel(hackathon_id=1L)]

        mock_db = Mock()
        mock_db.find_all_objects_by.return_value = admin_email_test
        mock_db.find_all_objects.return_value = admin_user_hackathon_rel

        am = AdminManager(mock_db)
        with app.test_request_context('/', headers={"token": token_value}):
            g.admin = AdminUser(id=1, name='testadmin')
            self.assertFalse(am.validate_admin_hackathon_request(2))
            mock_db.find_all_objects_by.assert_called_once_with(AdminEmail, admin_id=1)
            mock_db.find_all_objects.assert_called_once_with(AdminUserHackathonRel, ANY)


    '''test method : check_admin_hackathon_authority'''

    @patch.object(AdminManager, 'validate_admin_hackathon_request', return_value=True)
    def test_check_admin_hackathon_authority_hearder_miss_hackathon_id(self, mock_method):
        with app.test_request_context('/'):
            self.assertFalse(admin_manager.validate_hackathon_name())
            self.assertEqual(mock_method.call_count, 0)

    @patch.object(AdminManager, 'validate_admin_hackathon_request', return_value=True)
    def test_check_admin_hackathon_authority_hearder_hackathon_id_is_not_num(self, mock_method):
        with app.test_request_context('/', headers={"hackathon_id": "test"}):
            self.assertFalse(admin_manager.validate_hackathon_name())
            self.assertEqual(mock_method.call_count, 0)

    @patch.object(AdminManager, 'validate_admin_hackathon_request', return_value=False)
    def test_check_admin_hackathon_authority_faild(self, mock_thethod):
        with app.test_request_context('/', headers={"hackathon_id": 1}):
            self.assertFalse(admin_manager.validate_hackathon_name())
            mock_thethod.assert_called_once_with(1)

    @patch.object(AdminManager, 'validate_admin_hackathon_request', return_value=True)
    def test_check_admin_hackathon_authority_success(self, mock_thethod):
        with app.test_request_context('/', headers={"hackathon_id": 1}):
            self.assertTrue(admin_manager.validate_hackathon_name())
            mock_thethod.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()

