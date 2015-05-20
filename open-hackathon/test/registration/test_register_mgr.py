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
import datetime
from hackathon.enum import RGStatus, EStatus
from hackathon.hack import HackathonManager
from hackathon.hackathon_response import *
from hackathon.functions import get_now
import unittest
from hackathon.registration.register_mgr import RegisterManger, register_manager
from hackathon.database.models import UserHackathonRel, UserEmail, Hackathon, Experiment
from hackathon import app
from mock import Mock, ANY, patch
import mock
from flask import g


class TestUserHackathonRelManager(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        pass


    '''test method get_UserHackathonRel_list'''

    def test_get_UserHackathonRel_list_result_empty(self):
        db_adapter = Mock()
        db_adapter.find_all_objects_by.return_value = []
        rm = RegisterManger(db_adapter)
        with app.test_request_context('/'):
            self.assertEqual(rm.get_all_registration_by_hackathon_id(1), [])

    def test_get_UserHackathonRel_list_result_not_empty(self):
        db_adapter = Mock()
        UserHackathonRel1 = UserHackathonRel(id=1, real_name='test1', email='test2@test2.com', hackathon_id=1)
        UserHackathonRel2 = UserHackathonRel(id=2, real_name='test2', email='test2@test2.com', hackathon_id=1)
        db_adapter.find_all_objects_by.return_value = [UserHackathonRel1, UserHackathonRel2]
        rm = RegisterManger(db_adapter)
        with app.test_request_context('/'):
            self.assertEqual(len(rm.get_all_registration_by_hackathon_id(1)), 2)
            db_adapter.find_all_objects_by.assert_called_once_with(UserHackathonRel, hackathon_id=1)

    '''test method create_hackathon'''

    def test_create_hackathon_lost_args(self):
        args = {"a": "b"}
        hackathon = 'test_hackathon'
        self.assertEqual(register_manager.create_registration(hackathon, args), bad_request("user id invalid"))


    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    def test_create_hackathon_register_already_exist(self, get_method):
        args = {'user_id': 1}
        hackathon = Hackathon(id=1)
        register = UserHackathonRel(id=1, deleted=0)
        get_method.return_value = register
        self.assertEqual(register_manager.create_registration(hackathon, args), register.dic())
        get_method.assert_called_once_with(1, 1)


    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    def test_create_hackathon_register_registration_not_begin(self, get_method):
        args = {'user_id': 1}
        hackathon = Hackathon(id=1, registration_start_time=get_now() + datetime.timedelta(seconds=30))
        get_method.retrun_value = None
        self.assertEqual(register_manager.create_registration(hackathon, args),
                         precondition_failed("hackathon registration not opened", friendly_message="报名尚未开始"))
        get_method.assert_called_once_with(1, 1)


    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    def test_create_hackathon_register_registration_already_finished(self, get_method):
        get_method.retrun_value = None
        args = {'user_id': 1}
        hackathon = Hackathon(id=1,
                              registration_start_time=get_now() - datetime.timedelta(seconds=30),
                              registration_end_time=get_now() - datetime.timedelta(seconds=30))
        self.assertEqual(register_manager.create_registration(hackathon, args),
                         precondition_failed("hackathon registration has ended", friendly_message="报名已经结束"))
        get_method.assert_called_once_with(1, 1)


    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    @patch.object(HackathonManager, 'is_auto_approve')
    def test_create_hackathon_register_registration_common_logic(self, auto_approve, get_method):
        args = {'user_id': 1}
        hackathon = Hackathon(id=1,
                              registration_start_time=get_now() - datetime.timedelta(seconds=30),
                              registration_end_time=get_now() + datetime.timedelta(seconds=30))
        get_method.retrun_value = None
        auto_approve.return_value = True

        db_adapter = Mock()
        new_register = UserHackathonRel(id=7, user_id=1, status=RGStatus.AUTO_PASSED, deleted=0)
        db_adapter.add_object_kwargs.return_value = new_register
        rm = RegisterManger(db_adapter)

        self.assertEqual(rm.create_registration(hackathon, args), new_register.dic())
        get_method.assert_called_once_with(1, 1)
        auto_approve.assert_called_once_with(hackathon)


    '''test method update_hackathon'''

    @patch.object(RegisterManger, 'get_registration_by_id')
    def test_update_register_not_found(self, get_method):
        args = {"id": 1}
        get_method.return_value = None
        self.assertEqual(register_manager.update_registration(args), not_found("registration not found"))


    @patch.object(RegisterManger, 'get_registration_by_id')
    def test_update_register_common_loginc(self, get_method):
        args = {"id": 7, "phone": "1234567", 'create_time': '2012-12-23 09:09:09'}

        register = UserHackathonRel(id=7, user_id=1, status=RGStatus.AUTO_PASSED, deleted=0)
        get_method.return_value = register

        db_adapter = Mock()
        db_adapter.update_object.return_value = ''
        rm = RegisterManger(db_adapter)

        with mock.patch('hackathon.registration.register_mgr.get_now') as get_now:
            get_now.return_value = "now"
            rm.update_registration(args)
            db_adapter.update_object.assert_called_once_with(ANY, phone='1234567', update_time='now')


    '''test method delete_registration'''

    def test_delete_registration_lost_id(self):
        args = {'a': 'b'}
        self.assertEqual(register_manager.delete_registration(args), bad_request("id not invalid"))

    def test_delete_registration_not_found(self):
        db_adapter = Mock()
        db_adapter.find_first_object_by.return_value = None
        rm = RegisterManger(db_adapter)
        args = {'id': 1}
        self.assertEqual(rm.delete_registration(args), ok())
        db_adapter.find_first_object_by.assert_called_once_with(UserHackathonRel, id == 1)

    def test_delete_registration_commom_logic(self):
        db_adapter = Mock()
        register = UserHackathonRel(id=1)
        db_adapter.find_first_object_by.return_value = register
        db_adapter.delete_object.return_value = ""
        rm = RegisterManger(db_adapter)
        args = {'id': 1}
        self.assertEqual(rm.delete_registration(args), ok())
        db_adapter.find_first_object_by.assert_called_once_with(UserHackathonRel, id == 1)
        db_adapter.delete_object.assert_called_once_with(register)


    ''' test method : get_registration_detail '''

    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    def test_get_registration_detail_None_rel(self, get_method):
        user_id = 1
        hackathon = Hackathon(id=1)
        get_method.return_value = None
        detail = {'hackathon': hackathon.dic()}
        self.assertEqual(register_manager.get_registration_detail(user_id, hackathon), detail)
        get_method.assert_called_once_with(1, 1)


    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    def test_get_registration_detail_None_expr(self, get_method):
        user_id = 1
        hackathon = Hackathon(id=1)

        rel = UserHackathonRel(id=1)
        get_method.return_value = rel
        detail = {'hackathon': hackathon.dic(), "registration": rel.dic()}

        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)

        self.assertEqual(rm.get_registration_detail(user_id, hackathon), detail)
        get_method.assert_called_once_with(1, 1)
        db_adapter.find_first_object.assert_called_once_with(Experiment, ANY, ANY, ANY)


    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    def test_get_registration_detail_common_logic(self, get_method):
        user_id = 1

        hackathon = Hackathon(id=1)
        rel = UserHackathonRel(id=1)
        expr = Experiment(id=1)
        detail = {'hackathon': hackathon.dic(), "registration": rel.dic(), "experiment": expr.dic()}

        get_method.return_value = rel
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = expr
        rm = RegisterManger(db_adapter)

        self.assertEqual(rm.get_registration_detail(user_id, hackathon), detail)
        get_method.assert_called_once_with(1, 1)
        db_adapter.find_first_object.assert_called_once_with(Experiment, ANY, ANY, ANY)


