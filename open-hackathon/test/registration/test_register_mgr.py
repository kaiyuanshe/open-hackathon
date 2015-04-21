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
from hackathon.registration.register_mgr import RegisterManger, register_manager
from hackathon.database.models import Register
from hackathon import app
from mock import Mock, ANY
import mock
from flask import g


class TestRegisterManager(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        pass


    '''test method get_register_list'''

    def test_get_register_list_result_empty(self):
        db_adapter = Mock()
        db_adapter.find_all_objects.return_value = []
        rm = RegisterManger(db_adapter)
        with app.test_request_context('/'):
            self.assertEqual(rm.get_register_list(1), [])

    def test_get_register_list_result_not_empty(self):
        db_adapter = Mock()
        register1 = Register(id=1, register_name='test1', email='test2@test2.com', hackathon_id=1)
        register2 = Register(id=2, register_name='test2', email='test2@test2.com', hackathon_id=1)
        db_adapter.find_all_objects.return_value = [register1, register2]
        rm = RegisterManger(db_adapter)
        with app.test_request_context('/'):
            self.assertEqual(len(rm.get_register_list(1)), 2)
            db_adapter.find_all_objects.assert_called_once_with(Register, ANY)


    '''test method get_register_by_id'''

    def test_get_register_by_id_no_registers(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)
        result = rm.get_register_by_id(id=1)
        self.assertEqual(result, {'errorcode': 404, 'message': 'bad request'})
        db_adapter.find_first_object.assert_called_once_with(Register, ANY)

    def test_get_register_by_id_success(self):
        db_adapter = Mock()
        test_register = Register(id=1, register_name='test', email='test@test.com', hackathon_id=1)
        db_adapter.find_first_object.return_value = test_register
        rm = RegisterManger(db_adapter)
        result = rm.get_register_by_id(id=1)
        self.assertEqual(result['register_name'], 'test')
        db_adapter.find_first_object.assert_called_once_with(Register, ANY)


    '''test methon create_or_update_register'''

    def test_create_or_update_register_exception_raised(self):
        db_adapter = Mock()
        rm = RegisterManger(db_adapter)
        result, code = rm.create_or_update_register(1, {'test': 'test'})
        self.assertEqual(result, {"error": "INTERNAL SERVER ERROR"})
        self.assertEqual(code, 500)
        self.assertEqual(db_adapter.find_first_object.call_count, 0)

    def test_create_or_update_register_create(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)

        with app.test_request_context('/'):
            g.hackathon_id = 1
            rm.create_or_update_register(1, {'email': 'test@test.com',
                                             'register_name': 'test',
                                             'description': 'test desciption'})
            db_adapter.find_first_object.assert_called_once_with(Register, ANY, ANY)
            self.assertEqual(db_adapter.update_object.call_count, 0)
            self.assertEqual(db_adapter.add_object_kwargs.call_count, 1)

    def test_create_or_update_register_update(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = Register(id=7,
                                                             register_name='test_origin',
                                                             email='test_origin@test.com',
                                                             description='test origin desciption',
                                                             enabled=1,
                                                             hackathon_id=1)
        rm = RegisterManger(db_adapter)
        with app.test_request_context('/'):
            g.hackathon_id = 1
            rm.create_or_update_register(1, {'email': 'test_final@test.com',
                                             'register_name': 'test_final',
                                             'enabled': 1,
                                             'description': 'test final desciption'})
            db_adapter.find_first_object.assert_called_once_with(Register, ANY, ANY)
            self.assertEqual(db_adapter.update_object.call_count, 1)
            self.assertEqual(db_adapter.add_object_kwargs.call_count, 0)


    '''test methon delete_register'''

    def test_delete_register_lost_args(self):
        db_adapter = Mock()
        rm = RegisterManger(db_adapter)
        result, code = rm.delete_register({'test': 'test'})
        self.assertEqual(result, {"error": "Bad request"})
        self.assertEqual(code, 400)

    def test_delete_register_already_remved(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)
        result, code = rm.delete_register({'id': 1})
        db_adapter.find_first_object.assert_called_once_with(Register, ANY)
        self.assertEqual(result, {"message": "already removed"})
        self.assertEqual(code, 200)

    def test_delete_register_exception_raised(self):
        db_adapter = Mock()
        db_adapter.delete_object.side_effect = Exception('Test!')
        rm = RegisterManger(db_adapter)
        result, code = rm.delete_register({'id': 1})
        self.assertEqual(result, {"error": "INTERNAL SERVER ERROR"})
        self.assertEqual(code, 500)
        self.assertEqual(db_adapter.find_first_object.call_count, 1)
        self.assertEqual(db_adapter.delete_object.call_count, 1)

    def test_delete_register_success(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = Register(id=7,
                                                             register_name='test_origin',
                                                             email='test_origin@test.com',
                                                             description='test origin desciption',
                                                             enabled=1,
                                                             hackathon_id=1)
        rm = RegisterManger(db_adapter)
        rm.delete_register({'id': 7})
        self.assertEqual(db_adapter.find_first_object.call_count, 1)
        self.assertEqual(db_adapter.delete_object.call_count, 1)


    '''test method get_register_after_login'''

    def test_get_register_after_login_none_register(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)
        result = rm.get_register_after_login(hackathon_id=1, user_id=1)
        self.assertIsNone(result)
        db_adapter.find_first_object.assert_called_once_with(Register, ANY, ANY)

    def test_get_register_after_login(self):
        test_register = Register(id=1, register_name='test', email='test@test.com', hackathon_id=1, user_id=1)
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = test_register
        rm = RegisterManger(db_adapter)
        result = rm.get_register_after_login(hackathon_id=1, user_id=1)
        self.assertEqual(result.register_name, 'test')
        db_adapter.find_first_object.assert_called_once_with(Register, ANY, ANY)


    '''test method check_email'''

    def test_check_email_already_exist(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)
        self.assertTrue(rm.check_email(1, 'test@test.com'))
        db_adapter.find_first_object.assert_called_once_with(Register, ANY, ANY)

    def test_check_email_available(self):
        test_register = Register(id=1, register_name='test', email='test@test.com', hackathon_id=1, user_id=1)
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = test_register
        rm = RegisterManger(db_adapter)
        self.assertFalse(rm.check_email(1, 'test@test.com'))
        db_adapter.find_first_object.assert_called_once_with(Register, ANY, ANY)

    '''test methon get_register_by_uid_or_rid_and_hid'''

    def test_get_register_by_uid_or_rid_and_hid_bad_request(self):
        db_adapter = Mock()
        rm = RegisterManger(db_adapter)
        result11 = rm.get_register_by_rid_or_uid_and_hid({})
        result12 = rm.get_register_by_rid_or_uid_and_hid({'hid': 1})
        result13 = rm.get_register_by_rid_or_uid_and_hid({'uid': 1})
        result14 = rm.get_register_by_rid_or_uid_and_hid({'test': 1})
        self.assertEqual(result11, {"errorcode": 400, "message": "bad request"})
        self.assertEqual(result12, {"errorcode": 400, "message": "bad request"})
        self.assertEqual(result13, {"errorcode": 400, "message": "bad request"})
        self.assertEqual(result14, {"errorcode": 400, "message": "bad request"})

    def test_get_register_by_rid_or_uid_and_hid_give_rid(self):
        test_register = Register(id=1, register_name='test', email='test@test.com', hackathon_id=1)
        with mock.patch('hackathon.registration.register_mgr.RegisterManger.get_register_by_id') as get_register_by_id:
            get_register_by_id.return_value = test_register
            result = register_manager.get_register_by_rid_or_uid_and_hid({'rid': 1})
            self.assertEqual(result.register_name, 'test')
            get_register_by_id.assert_called_once_with(1)

    def test_get_register_by_rid_or_uid_and_hid_give_uid_and_hid(self):
        db_adapter = Mock()
        test_register = Register(id=1, register_name='test', email='test@test.com', hackathon_id=1)
        db_adapter.find_first_object.return_value = test_register
        rm = RegisterManger(db_adapter)
        result = rm.get_register_by_rid_or_uid_and_hid({'uid': 1, 'hid': 1})
        self.assertEqual(result['register_name'], 'test')
        db_adapter.find_first_object.assert_called_once_with(Register, ANY, ANY)

    def test_get_register_by_rid_or_uid_and_hid_give_uid_and_hid_none_register(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)
        result = rm.get_register_by_rid_or_uid_and_hid({'uid': 1, 'hid': 1})
        self.assertEqual(result, {"errorcode": 404, "message": "not found"})
        db_adapter.find_first_object.assert_called_once_with(Register, ANY, ANY)