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
from hackathon.enum import RGStatus
from hackathon.hack import HackathonManager
from hackathon.hackathon_response import bad_request, precondition_failed, not_found, ok
import unittest
from hackathon.database.models import UserHackathonRel, Hackathon, Experiment
from hackathon import app, RequiredFeature
from mock import Mock, ANY, patch
import mock


class TestExperimengManager(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        pass

    def test_get_expr_status(self):
        expr_id = 11
        expr_manager = RequiredFeature("expr_manager")
        result = expr_manager.get_expr_status(expr_id)

    '''test method get_UserHackathonRel_list'''
    #
    # def test_get_UserHackathonRel_list_result_empty(self):
    #     db_adapter = Mock()
    #     db_adapter.find_all_objects_by.return_value = []
    #     rm = RegisterManager(db_adapter)
    #     with app.test_request_context('/'):
    #         self.assertEqual(rm.get_all_registration_by_hackathon_id(1), [])
    #
    # def test_get_UserHackathonRel_list_result_not_empty(self):
    #     db_adapter = Mock()
    #     UserHackathonRel1 = UserHackathonRel(id=1, real_name='test1', email='test2@test2.com', hackathon_id=1)
    #     UserHackathonRel2 = UserHackathonRel(id=2, real_name='test2', email='test2@test2.com', hackathon_id=1)
    #     db_adapter.find_all_objects_by.return_value = [UserHackathonRel1, UserHackathonRel2]
    #     rm = RegisterManager(db_adapter)
    #     with app.test_request_context('/'):
    #         self.assertEqual(len(rm.get_all_registration_by_hackathon_id(1)), 2)
    #         db_adapter.find_all_objects_by.assert_called_once_with(UserHackathonRel, hackathon_id=1)

    '''test method create_hackathon'''
