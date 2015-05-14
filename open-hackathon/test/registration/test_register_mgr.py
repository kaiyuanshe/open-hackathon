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
from hackathon.enum import RGStatus
from hackathon.hack import HackathonManager
from hackathon.hackathon_response import *

sys.path.append("../src/hackathon")
import unittest
from hackathon.registration.register_mgr import RegisterManger, register_manager
from hackathon.database.models import UserHackathonRel, UserEmail, Hackathon
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
    def test_create_hackathon_register_already_exist(self,get_method):
        args = {'user_id': 1}
        hackathon = Hackathon(id=1)
        register = UserHackathonRel(id=1, deleted=0)
        get_method.return_value = register
        self.assertEqual(register_manager.create_registration(hackathon, args), register.dic())
        get_method.assert_called_once_with(1, 1)


    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    def test_create_hackathon_register_registration_not_begin(self, get_method):
        args = {'user_id': 1}
        hackathon = Hackathon(id=1, registration_start_time=datetime.get_now() + datetime.timedelta(seconds=30))
        get_method.retrun_value = None
        self.assertEqual(register_manager.create_registration(hackathon, args),
                         precondition_failed("hackathon registration not opened", friendly_message="报名尚未开始"))
        get_method.assert_called_once_with(1, 1)


    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    def test_create_hackathon_register_registration_already_finished(self,get_method):
        get_method.retrun_value = None
        args = {'user_id': 1}
        hackathon = Hackathon(id=1,
                              registration_start_time=datetime.get_now() - datetime.timedelta(seconds=30),
                              registration_end_time=datetime.get_now() - datetime.timedelta(seconds=30))
        self.assertEqual(register_manager.create_registration(hackathon, args),
                         precondition_failed("hackathon registration has ended", friendly_message="报名已经结束"))
        get_method.assert_called_once_with(1, 1)


    @patch.object(RegisterManger, 'get_registration_by_user_and_hackathon')
    @patch.object(HackathonManager, 'is_auto_approve')
    def test_create_hackathon_register_registration_common_logic(self,auto_approve,get_method):
        args = {'user_id': 1}
        hackathon = Hackathon(id=1,
                              registration_start_time=datetime.get_now() - datetime.timedelta(seconds=30),
                              registration_end_time=datetime.get_now() + datetime.timedelta(seconds=30))
        get_method.retrun_value = None
        auto_approve.return_value = True

        db_adapter = Mock()
        new_register = UserHackathonRel(id=7,user_id=1,status=RGStatus.AUTO_PASSED,deleted=0)
        db_adapter.add_object_kwargs.return_value = new_register
        rm = RegisterManger(db_adapter)

        self.assertEqual(rm.create_registration(hackathon,args),new_register.dic())
        get_method.assert_called_once_with(1, 1)
        auto_approve.assert_called_once_with(hackathon)


    '''test method update_hackathon'''

    @patch.object(RegisterManger, 'get_registration_by_id')
    def test_update_register_not_found(self,get_method):
        args = {"id": 1}
        get_method.return_value = None
        self.assertEqual(register_manager.update_registration(args), not_found("registration not found"))


    @patch.object(RegisterManger, 'get_registration_by_id')
    @patch.object(datetime.datetime,'utcnow')
    def test_update_register_common_loginc(self, now, get_method):
        args = {"id": 7, "phone":"1234567", 'create_time':'2012-12-23 09:09:09'}

        register = UserHackathonRel(id=7,user_id=1,status=RGStatus.AUTO_PASSED,deleted=0)
        get_method.return_value = register

        db_adapter = Mock()
        db_adapter.update_object.return_value = ''
        rm = RegisterManger(db_adapter)

        now.return_value = '2012-12-23 09:09:09'

        items = {'phone': 1234567,'update_time': '2012-12-23 09:09:09'}

        db_adapter.update_object.assert_called_once_with(ANY,items)




















            #
            #
            # '''test methon delete_UserHackathonRel'''
            #
            # def test_delete_UserHackathonRel_lost_args(self):
            # db_adapter = Mock()
            #     rm = RegisterManger(db_adapter)
            #     result, code = rm.delete_registration({'test': 'test'})
            #     self.assertEqual(result, {"error": "Bad request"})
            #     self.assertEqual(code, 400)
            #
            # def test_delete_UserHackathonRel_already_remved(self):
            #     db_adapter = Mock()
            #     db_adapter.find_first_object.return_value = None
            #     rm = RegisterManger(db_adapter)
            #     result, code = rm.delete_registration({'id': 1})
            #     db_adapter.find_first_object.assert_called_once_with(UserHackathonRel, ANY)
            #     self.assertEqual(result, {"message": "already removed"})
            #     self.assertEqual(code, 200)
            #
            # def test_delete_UserHackathonRel_exception_raised(self):
            #     db_adapter = Mock()
            #     db_adapter.delete_object.side_effect = Exception('Test!')
            #     rm = RegisterManger(db_adapter)
            #     result, code = rm.delete_registration({'id': 1})
            #     self.assertEqual(result, {"error": "INTERNAL SERVER ERROR"})
            #     self.assertEqual(code, 500)
            #     self.assertEqual(db_adapter.find_first_object.call_count, 1)
            #     self.assertEqual(db_adapter.delete_object.call_count, 1)
            #
            # def test_delete_UserHackathonRel_success(self):
            #     db_adapter = Mock()
            #     db_adapter.find_first_object.return_value = UserHackathonRel(id=7,
            #                                                          UserHackathonRel_name='test_origin',
            #                                                          email='test_origin@test.com',
            #                                                          description='test origin desciption',
            #                                                          enabled=1,
            #                                                          hackathon_id=1)
            #     rm = RegisterManger(db_adapter)
            #     rm.delete_registration({'id': 7})
            #     self.assertEqual(db_adapter.find_first_object.call_count, 1)
            #     self.assertEqual(db_adapter.delete_object.call_count, 1)
            #
            #
            # '''test method check_email'''
            #
            # def test_check_email_already_exist(self):
            #     db_adapter = Mock()
            #     db_adapter.find_first_object.return_value = None
            #     rm = RegisterManger(db_adapter)
            #     self.assertTrue(rm.is_email_registered(1, 'test@test.com'))
            #     db_adapter.find_first_object.assert_called_once_with(UserHackathonRel, ANY, ANY)
            #
            # def test_check_email_available(self):
            #     test_UserHackathonRel = UserHackathonRel(id=1, real_name='test', email='test@test.com', hackathon_id=1, user_id=1)
            #     db_adapter = Mock()
            #     db_adapter.find_first_object.return_value = test_UserHackathonRel
            #     rm = RegisterManger(db_adapter)
            #     self.assertFalse(rm.is_email_registered(1, 'test@test.com'))
            #     db_adapter.find_first_object.assert_called_once_with(UserHackathonRel, ANY, ANY)
            #
            #
            # '''test methon get_UserHackathonRel_by_uid_or_rid_and_hid'''
            #
            # def test_get_UserHackathonRel_by_uid_or_rid_and_hid_bad_request(self):
            #     db_adapter = Mock()
            #     rm = RegisterManger(db_adapter)
            #     result11 = rm.get_registration_detail({})
            #     result12 = rm.get_registration_detail({'hid': 1})
            #     result13 = rm.get_registration_detail({'uid': 1})
            #     result14 = rm.get_registration_detail({'test': 1})
            #     self.assertEqual(result11, {"errorcode": 400, "message": "bad request, when calling get UserHackathonRel by rid or hid and uid"})
            #     self.assertEqual(result12, {"errorcode": 400, "message": "bad request, when calling get UserHackathonRel by rid or hid and uid"})
            #     self.assertEqual(result13, {"errorcode": 400, "message": "bad request, when calling get UserHackathonRel by rid or hid and uid"})
            #     self.assertEqual(result14, {"errorcode": 400, "message": "bad request, when calling get UserHackathonRel by rid or hid and uid"})
            #
            # def test_get_UserHackathonRel_by_rid_or_uid_and_hid_give_rid(self):
            #     test_UserHackathonRel = UserHackathonRel(id=1, real_name='test', email='test@test.com', hackathon_id=1)
            #     with mock.patch('hackathon.registration.UserHackathonRel_mgr.RegisterManger.get_UserHackathonRel_by_id') as get_UserHackathonRel_by_id:
            #         get_UserHackathonRel_by_id.return_value = test_UserHackathonRel
            #         result = register_manager.get_UserHackathonRel_by_rid_or_uid_and_hid({'rid': 1})
            #         self.assertEqual(result.real_name, 'test')
            #         get_UserHackathonRel_by_id.assert_called_once_with(1)
            #
            # def test_get_UserHackathonRel_by_rid_or_uid_and_hid_give_uid_and_hid(self):
            #     db_adapter = Mock()
            #     test_UserHackathonRel = UserHackathonRel(id=1, real_name='test', email='test@test.com', hackathon_id=1)
            #     db_adapter.find_first_object.return_value = test_UserHackathonRel
            #     rm = RegisterManger(db_adapter)
            #     result = rm.get_registration_detail({'uid': 1, 'hid': 1})
            #     self.assertEqual(result['real_name'], 'test')
            #     db_adapter.find_first_object.assert_called_once_with(UserHackathonRel, ANY, ANY)
            #
            # def test_get_UserHackathonRel_by_rid_or_uid_and_hid_give_uid_and_hid_none_UserHackathonRel(self):
            #     db_adapter = Mock()
            #     db_adapter.find_first_object.return_value = None
            #     rm = RegisterManger(db_adapter)
            #     result = rm.get_registration_detail({'uid': 1, 'hid': 1})
            #     self.assertEqual(result, {"errorcode": 404, "message": "UserHackathonRel not found"})
            #     db_adapter.find_first_object.assert_called_once_with(UserHackathonRel, ANY, ANY)
            #
            #
            # '''test method : deal_with_user_and_UserHackathonRel_when_login'''
            #
            # def test_deal_with_user_and_UserHackathonRel_when_login_success(self):
            #     user_email = UserEmail(id=1, email='test@test.com', user_id=1)
            #     user = mock.MagicMock(id=1, emails=[user_email])
            #     db_adapter = Mock()
            #     rm = RegisterManger(db_adapter)
            #
            #     with mock.patch(
            #             'hackathon.registration.UserHackathonRel_mgr.RegisterManger.get_UserHackathonRel_by_emails_and_hid') as get_UserHackathonRel_by_emails_and_hid:
            #         uhr = UserHackathonRel(id=1, real_name='test_name')
            #         get_UserHackathonRel_by_emails_and_hid.return_value = uhr
            #         rm.deal_with_user_and_register_when_login(user, 1)
            #         get_UserHackathonRel_by_emails_and_hid.assert_called_once_with(1, ['test@test.com'])
            #         db_adapter.update_object(UserHackathonRel, ANY)
            #
            # def test_deal_with_user_and_UserHackathonRel_when_login_UserHackathonRel_None(self):
            #     user_email = UserEmail(id=1, email='test@test.com', user_id=1)
            #     user = mock.MagicMock(id=1, emails=[user_email])
            #     db_adapter = Mock()
            #     rm = RegisterManger(db_adapter)
            #
            #     with mock.patch(
            #             'hackathon.registration.UserHackathonRel_mgr.RegisterManger.get_UserHackathonRel_by_emails_and_hid') as get_UserHackathonRel_by_emails_and_hid:
            #         get_UserHackathonRel_by_emails_and_hid.return_value = None
            #         rm.deal_with_user_and_register_when_login(user, 1)
            #         get_UserHackathonRel_by_emails_and_hid.assert_called_once_with(1, ['test@test.com'])
            #         self.assertEqual(db_adapter.update_object.call_count, 0)
            #
            # def test_deal_with_user_and_UserHackathonRel_when_login_UserHackathonRel_user_id_not_none(self):
            #     user_email = UserEmail(id=1, email='test@test.com', user_id=1)
            #     user = mock.MagicMock(id=1, emails=[user_email])
            #     db_adapter = Mock()
            #     rm = RegisterManger(db_adapter)
            #
            #     with mock.patch(
            #             'hackathon.registration.UserHackathonRel_mgr.RegisterManger.get_UserHackathonRel_by_emails_and_hid') as get_UserHackathonRel_by_emails_and_hid:
            #         uhr = UserHackathonRel(id=1, real_name='test_name', user_id=1)
            #         get_UserHackathonRel_by_emails_and_hid.return_value = uhr
            #         rm.deal_with_user_and_register_when_login(user, 1)
            #         get_UserHackathonRel_by_emails_and_hid.assert_called_once_with(1, ['test@test.com'])
            #         self.assertEqual(db_adapter.update_object.call_count, 0)
            #
            #
            # '''test method deal_with_user_and_UserHackathonRel_when_create_UserHackathonRel'''
            # def test_deal_with_user_and_UserHackathonRel_when_create_UserHackathonRel_success(self):
            #     db_adapter = Mock()
            #     rm = RegisterManger(db_adapter)
            #     args = {'email':'test@test.com'}
            #     result = {'email':'test@test.com','user_id':1}
            #
            #     user_email = UserEmail(user_id=1)
            #     db_adapter.find_first_object.return_value= user_email
            #
            #     self.assertEqual(rm.deal_with_user_and_register_when_create_register(args),result)
            #     db_adapter.find_first_object.assert_called_once_with(UserEmail,ANY)
            #
            # def test_deal_with_user_and_UserHackathonRel_when_create_UserHackathonRel_user_email_none(self):
            #     db_adapter = Mock()
            #     rm = RegisterManger(db_adapter)
            #     args = {'email':'test@test.com'}
            #
            #     db_adapter.find_first_object.return_value= None
            #     self.assertEqual(rm.deal_with_user_and_register_when_create_register(args),args)
            #     db_adapter.find_first_object.assert_called_once_with(UserEmail,ANY)