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

sys.path.append("../../src/hackathon")
import unittest
from hackathon.user.user_mgr import UserManager
from hackathon.database import SQLAlchemyAdapter
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

        mock_db = Mock(spec=SQLAlchemyAdapter)
        mock_db.find_first_object_by.return_value = None

        um = UserManager(mock_db)

        with app.test_request_context('/api', headers={"token": token_value}):
            self.assertTrue("token" in request.headers)
            self.assertFalse(um.validate_request())
            mock_db.find_first_object_by.assert_called_once_with(UserToken, token=token_value)


    def test_validate_request_token_expired(self):
        token_value = "token_value"
        token = UserToken(token=token_value, user=None, expire_date=datetime.utcnow() - timedelta(seconds=30))

        mock_db = Mock(spec=SQLAlchemyAdapter)
        mock_db.find_first_object_by.return_value = token

        um = UserManager(mock_db)

        with app.test_request_context('/', headers={"token": token_value}):
            self.assertTrue("token" in request.headers)
            self.assertFalse(um.validate_request())
            self.assertEqual(mock_db.find_first_object_by.call_count, 1)
            mock_db.find_first_object_by.assert_called_once_with(UserToken, token=token_value)


    def test_validate_request_token_valid(self):
        token_value = "token_value"
        user = User(name="test_name")
        token = UserToken(token=token_value, user=user, expire_date=datetime.utcnow() + timedelta(seconds=30))

        mock_db = Mock(spec=SQLAlchemyAdapter)
        mock_db.find_first_object_by.return_value = token

        um = UserManager(mock_db)

        with app.test_request_context('/', headers={"token": token_value}):
            self.assertTrue("token" in request.headers)
            self.assertTrue(um.validate_request())
            mock_db.find_first_object_by.assert_called_once_with(UserToken, token=token_value)
            self.assertEqual(g.user, user)