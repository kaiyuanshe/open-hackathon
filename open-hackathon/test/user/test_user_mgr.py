import sys

sys.path.append("../src/hackathon")
import unittest
from hackathon.user.user_mgr import UserManager
from hackathon.database.models import UserToken, User
from hackathon import app
from mock import Mock
from datetime import datetime, timedelta
from flask import request, g


class UserManagerTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        pass

    def test_validate_request_if_token_missing(self):
        um = UserManager(None)
        '''more args for app.text_request_context:
                 path='/', base_url=None, query_string=None,
                 method='GET', input_stream=None, content_type=None,
                 content_length=None, errors_stream=None, multithread=False,
                 multiprocess=False, run_once=False, headers=None, data=None,
                 environ_base=None, environ_overrides=None, charset='utf-8'
        '''
        with app.test_request_context('/', headers=None):
            self.assertFalse("token" in request.headers)
            self.assertFalse(um.validate_request())


    def test_validate_request_token_not_found(self):
        token_value = "token_value"

        # mock pu
        mock_db = Mock()
        mock_db.find_first_object_by.return_value = None

        um = UserManager(mock_db)

        with app.test_request_context('/', headers={"token": token_value}):
            self.assertTrue("token" in request.headers)
            self.assertFalse(um.validate_request())
            self.assertEqual(mock_db.find_first_object_by.call_count, 1)

    def test_validate_request_token_expired(self):
        token_value = "token_value"
        token = UserToken(token=token_value, user=None, expire_date=datetime.utcnow() - timedelta(seconds=30))

        # mock pu
        mock_db = Mock()
        mock_db.find_first_object_by.return_value = token

        um = UserManager(mock_db)

        with app.test_request_context('/', headers={"token": token_value}):
            self.assertTrue("token" in request.headers)
            self.assertFalse(um.validate_request())
            self.assertEqual(mock_db.find_first_object_by.call_count, 1)

    def test_validate_request_token_valid(self):
        token_value = "token_value"
        user = User(name="test_name")
        token = UserToken(token=token_value, user=user, expire_date=datetime.utcnow() + timedelta(seconds=30))

        # mock pu
        mock_db = Mock()
        mock_db.find_first_object_by.return_value = token

        um = UserManager(mock_db)

        with app.test_request_context('/', headers={"token": token_value}):
            self.assertTrue("token" in request.headers)
            self.assertTrue(um.validate_request())
            self.assertEqual(mock_db.find_first_object_by.call_count, 1)
            self.assertEqual(g.user, user)