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
import datetime
from pytz import utc
import pytz

sys.path.append("../../src/hackathon")
import unittest
from hackathon.admin.admin_mgr import AdminManager
from hackathon.database.models import User, UserEmail, Hackathon, AdminHackathonRel
from hackathon import app, RequiredFeature
from mock import Mock, ANY, patch
import mock

from flask import g
from hackathon.hackathon_response import bad_request, precondition_failed, not_found, ok, internal_server_error




class AdminManagerTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        pass

    admin_manager = RequiredFeature("admin_manager")


    '''test method create admin '''

    def test_create_admin_bad_request(self):
        args = {}
        self.assertEqual(self.admin_manager.create_admin(args), bad_request("email invalid"))

    def test_create_admin_email_missed(self):
        args = {'email': 'test@test.com'}
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        am = AdminManager(db_adapter)

        self.assertEqual(am.create_admin(args), not_found("email does not exist in DB"))
        db_adapter.find_first_object.assert_called_once_with(UserEmail, ANY)

    def test_create_admin_already_exist(self):
        args = {'email': 'test@test.com'}
        user = User(id=7)
        user_email = UserEmail(id=7, user=user, user_id=7)

        db_adapter = Mock()
        db_adapter.find_first_object.side_effect = [user_email, "test"]
        am = AdminManager(db_adapter)

        with app.test_request_context('/', headers=None):
            g.hackathon = Hackathon(id=7)
            self.assertEqual(am.create_admin(args), ok())
            self.assertEqual(db_adapter.find_first_object.call_count, 2)

    def test_create_admin_common_logic(self):
        args = {'email': 'test@test.com', 'role_type': 1, 'remarks': 'test'}
        user = User(id=7)
        user_email = UserEmail(id=7, user=user, user_id=7)

        db_adapter = Mock()
        db_adapter.find_first_object.side_effect = [user_email, None]
        db_adapter.add_object.return_value = "success"
        am = AdminManager(db_adapter)

        with app.test_request_context('/', headers=None):
            g.hackathon = Hackathon(id=7)
            self.assertEqual(am.create_admin(args), ok())
            self.assertEqual(db_adapter.find_first_object.call_count, 2)
            db_adapter.add_object.assert_called_once_with(ANY)


    '''test method validate_updated_args '''

    def test_validate_updated_args_invalid_id(self):
        args = {}
        status, return_info = self.admin_manager.validate_updated_args(args)
        self.assertFalse(status)
        self.assertEqual(return_info, bad_request("invalid id"))

    def test_validate_updated_args_ahl_not_found(self):
        args = {'id': 7}
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        am = AdminManager(db_adapter)
        status, return_info = am.validate_updated_args(args)
        self.assertFalse(status)
        self.assertEqual(return_info, not_found("ahl does not exist"))
        db_adapter.find_first_object.assert_called_once_with(AdminHackathonRel, ANY)

    def test_validate_updated_args_common_logic(self):
        args = {'id': 7}
        ahl = AdminHackathonRel(id=7)
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = ahl
        am = AdminManager(db_adapter)
        status, return_info = am.validate_updated_args(args)
        self.assertTrue(status)
        self.assertEqual(return_info, ahl)
        db_adapter.find_first_object.assert_called_once_with(AdminHackathonRel, ANY)


    '''test method update_admin '''

    @patch.object(AdminManager, 'validate_updated_args', return_value=(True, ''))
    @patch.object(AdminManager, 'generate_update_items', return_value={'test': 'test'})
    def test_update_admin_raise_exception(self, generate_update_items, validate_updated_args):
        self.assertEqual(1, 1)
        db_adapter = Mock()
        args = {'test': 'test'}
        db_adapter.update_object.side_effect = [Exception]
        am = AdminManager(db_adapter)
        self.assertEqual(am.update_admin(args), internal_server_error(ANY))
        generate_update_items.assert_called_once_with(args)
        validate_updated_args.assert_called_once_with(args)

    @patch.object(AdminManager, 'validate_updated_args', return_value=(True, AdminHackathonRel(id=7)))
    def test_update_admin_common_logic(self, validate_updated_args):
        db_adapter = Mock()
        args = {'role_type': 1, 'email': 'test'}
        db_adapter.update_object.return_value = 'passed'
        am = AdminManager(db_adapter)

        with mock.patch('hackathon.admin.admin_mgr.get_now') as get_now:
            get_now.return_value = "now"
            self.assertEqual(am.update_admin(args), ok('update hackathon admin success'))
            validate_updated_args.assert_called_once_with(args)
            db_adapter.update_object.assert_called_once_with(ANY, role_type=1, update_time='now')


    '''test method validate_deleted_args'''

    def test_validate_deleted_args_already_missed(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        am = AdminManager(db_adapter)

        status, return_info = am.validate_deleted_args(1)
        self.assertFalse(status)
        self.assertEqual(return_info, ok())
        db_adapter.find_first_object(AdminHackathonRel, ANY)

    def test_validate_deleted_args_delete_creator(self):
        ahl = AdminHackathonRel(id=7, user_id=7, hackathon_id=7)
        hackathon = Hackathon(id=7, creator_id=7)

        db_adapter = Mock()
        db_adapter.find_first_object.side_effect = [ahl, hackathon]
        am = AdminManager(db_adapter)

        status, return_info = am.validate_deleted_args(1)
        self.assertFalse(status)
        self.assertEqual(return_info, precondition_failed("hackathon creator can not be deleted"))
        self.assertEqual(db_adapter.find_first_object.call_count, 2)


    '''test method delete_admin'''

    @patch.object(AdminManager, 'validate_deleted_args', return_value=(True, ''))
    def test_delete_admin_raise_exception(self, validate_deleted_args):
        db_adapter = Mock()
        db_adapter.delete_all_objects.side_effect = [Exception]
        am = AdminManager(db_adapter)
        self.assertEqual(am.delete_admin(1), internal_server_error(ANY))
        validate_deleted_args.assert_called_once_with(1)

    @patch.object(AdminManager, 'validate_deleted_args', return_value=(True, ''))
    def test_delete_admin_common_logic(self, validate_deleted_args):
        db_adapter = Mock()
        db_adapter.delete_all_objects.side_effect = 'passed'
        am = AdminManager(db_adapter)
        self.assertEqual(am.delete_admin(1), ok())
        validate_deleted_args.assert_called_once_with(1)
