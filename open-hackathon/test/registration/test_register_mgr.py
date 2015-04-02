import sys

sys.path.append("../src/hackathon")
import unittest
from hackathon.registration.register_mgr import RegisterManger
from hackathon.database.models import Register
from hackathon import app
from mock import Mock, ANY
from flask import g
from json import JSONDecoder


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

    def test_get_register_by_id_lost_args(self):
        db_adapter = Mock()
        rm = RegisterManger(db_adapter)
        result, code = rm.get_register_by_id(test='test')
        self.assertEqual(result, {"error": "Bad request"})
        self.assertEqual(code, 400)

    def test_get_register_by_id_no_registers(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)
        result, code = rm.get_register_by_id(id=1)
        self.assertEqual(result, {"error": "REGISTER NOT FOUND"})
        self.assertEqual(code, 400)
        db_adapter.find_first_object.assert_called_once_with(Register, ANY)

    def test_get_register_by_id_success(self):
        db_adapter = Mock()
        test_register = Register(id=1, register_name='test', email='test@test.com', hackathon_id=1)
        db_adapter.find_first_object.return_value = test_register
        rm = RegisterManger(db_adapter)
        result = JSONDecoder().decode(rm.get_register_by_id(id=1))
        self.assertEqual(result['register_name'], 'test')
        db_adapter.find_first_object.assert_called_once_with(Register, ANY)


    '''test methon create_or_update_register'''

    def test_create_or_update_register_exception_raised(self):
        db_adapter = Mock()
        rm = RegisterManger(db_adapter)
        result, code = rm.create_or_update_register(test='test')
        self.assertEqual(result, {"error": "INTERNAL SERVER ERROR"})
        self.assertEqual(code, 500)
        self.assertEqual(db_adapter.find_first_object.call_count, 0)


    def test_create_or_update_register_create(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)

        with app.test_request_context('/'):
            g.hackathon_id = 1
            rm.create_or_update_register(email='test@test.com',
                                         register_name='test',
                                         description='test desciption')
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
            rm.create_or_update_register(email='test_final@test.com',
                                         register_name='test_final',
                                         enabled=1,
                                         description='test final desciption')
            db_adapter.find_first_object.assert_called_once_with(Register, ANY, ANY)
            self.assertEqual(db_adapter.update_object.call_count, 1)
            self.assertEqual(db_adapter.add_object_kwargs.call_count, 0)

    '''test methon delete_register'''

    def test_delete_register_lost_args(self):
        db_adapter = Mock()
        rm = RegisterManger(db_adapter)
        result, code = rm.delete_register(test='test')
        self.assertEqual(result, {"error": "Bad request"})
        self.assertEqual(code, 400)

    def test_delete_register_already_remved(self):
        db_adapter = Mock()
        db_adapter.find_first_object.return_value = None
        rm = RegisterManger(db_adapter)
        result, code = rm.delete_register(id=1)
        db_adapter.find_first_object.assert_called_once_with(Register, ANY)
        self.assertEqual(result, {"message": "already removed"})
        self.assertEqual(code, 200)

    def test_delete_register_exception_raised(self):
        db_adapter = Mock()
        db_adapter.delete_object.side_effect = Exception('Test!')
        rm = RegisterManger(db_adapter)
        result, code = rm.delete_register(id=1)
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
        rm.delete_register(id=7)
        self.assertEqual(db_adapter.find_first_object.call_count, 1)
        self.assertEqual(db_adapter.delete_object.call_count, 1)
