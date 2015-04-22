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
from hackathon.user.login import GithubLogin, QQLogin, WeiboLogin, GitcafeLogin
from hackathon import app
from mock import Mock, ANY
import mock
from hackathon.database.models import User, UserToken, Hackathon, Register
from hackathon.user.login import LoginProviderBase


class TestToken:
    token = 'test_token'


class UserLoginTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        pass

    '''test method return_details'''

    def test_return_details_success(self):
        user = User(name="test_name", id=1)
        token = UserToken(token='test_token', user_id=1)
        user_with_token = {'user': user, 'token': token}
        args = {'hackathon_name': 'test_hackathon_name'}

        with mock.patch('hackathon.user.user_mgr.UserManager.get_user_detail_info') as get_user_detail_info:
            detail = {'details': "details"}
            get_user_detail_info.return_value = detail
            with mock.patch('hackathon.hack.HackathonManager.get_hackathon_by_name') as get_hackathon_by_name:
                hackathon = Hackathon(id=1, name='test_hackathon')
                get_hackathon_by_name.return_value = hackathon
                with mock.patch(
                        'hackathon.registration.register_mgr.RegisterManger.get_register_by_rid_or_uid_and_hid') as get_register_by_rid_or_uid_and_hid:
                    register = Register(id=1, register_name='test', email='test@test.com', hackathon_id=1)
                    get_register_by_rid_or_uid_and_hid.return_value = register
                    with mock.patch(
                            'hackathon.registration.register_mgr.RegisterManger.deal_with_user_and_register_when_login') as deal_with_user_and_register_when_login:
                        deal_with_user_and_register_when_login.return_value = None

                        result = {}
                        detail['token'] = 'test_token'
                        result['user'] = detail
                        result['hackathon'] = hackathon.dic()
                        result['registration'] = register.dic()

                        self.assertEqual(LoginProviderBase().return_details(user_with_token, args), result)
                        get_user_detail_info.assert_called_once_with(user)
                        get_hackathon_by_name.assert_called_once_with('test_hackathon_name')
                        get_register_by_rid_or_uid_and_hid.assert_called_once_with({'hid': 1, 'uid': 1})
                        deal_with_user_and_register_when_login.assert_called_once_with(user, 1)


    def test_return_details_hackathon_name_not_fount(self):
        user = User(name="test_name", id=1)
        token = UserToken(token='test_token', user_id=1)
        user_with_token = {'user': user, 'token': token}
        args = {'hackathon_name': 'test_hackathon_name'}

        with mock.patch('hackathon.user.user_mgr.UserManager.get_user_detail_info') as get_user_detail_info:
            detail = {'details': "details"}
            get_user_detail_info.return_value = detail
            with mock.patch('hackathon.hack.HackathonManager.get_hackathon_by_name') as get_hackathon_by_name:
                get_hackathon_by_name.return_value = None

                result = {"errorcode": 400, "message": "bad request : hackathon_name does not exist in DB"}
                self.assertEqual(LoginProviderBase().return_details(user_with_token, args), result)
                get_user_detail_info.assert_called_once_with(user)
                get_hackathon_by_name.assert_called_once_with('test_hackathon_name')


    def test_return_details_get_register_by_email(self):
        # logic : get register by hid and uid returns None , Then get register by emails and hid is not None

        user = User(name="test_name", id=1)
        token = UserToken(token='test_token', user_id=1)
        user_with_token = {'user': user, 'token': token}
        args = {'hackathon_name': 'test_hackathon_name'}

        with mock.patch('hackathon.user.user_mgr.UserManager.get_user_detail_info') as get_user_detail_info:
            detail = {'details': "details"}
            get_user_detail_info.return_value = detail
            with mock.patch('hackathon.hack.HackathonManager.get_hackathon_by_name') as get_hackathon_by_name:
                hackathon = Hackathon(id=1, name='test_hackathon')
                get_hackathon_by_name.return_value = hackathon
                # get register by hid and uid returns None
                with mock.patch(
                        'hackathon.registration.register_mgr.RegisterManger.get_register_by_rid_or_uid_and_hid') as get_register_by_rid_or_uid_and_hid:
                    get_register_by_rid_or_uid_and_hid.return_value = None
                    #Then get register by emails and hid is not None
                    with mock.patch(
                            'hackathon.registration.register_mgr.RegisterManger.get_register_by_emails_and_hid') as get_register_by_emails_and_hid:
                        register = Register(id=1, register_name='test', email='test@test.com', hackathon_id=1)
                        get_register_by_emails_and_hid.return_value = register
                        with mock.patch(
                                'hackathon.registration.register_mgr.RegisterManger.deal_with_user_and_register_when_login') as deal_with_user_and_register_when_login:
                            deal_with_user_and_register_when_login.return_value = None

                            result = {}
                            detail['token'] = 'test_token'
                            result['user'] = detail
                            result['hackathon'] = hackathon.dic()
                            result['registration'] = register.dic()

                            self.assertEqual(LoginProviderBase().return_details(user_with_token, args), result)
                            get_user_detail_info.assert_called_once_with(user)
                            get_hackathon_by_name.assert_called_once_with('test_hackathon_name')
                            get_register_by_rid_or_uid_and_hid.assert_called_once_with({'hid': 1, 'uid': 1})
                            get_register_by_emails_and_hid.assert_called_once_with(1, ANY)
                            deal_with_user_and_register_when_login.assert_called_once_with(user, 1)

    def test_return_details_get_register_none(self):
        # logic : get register by hid_uid and emails_hid are both return None

        user = User(name="test_name", id=1)
        token = UserToken(token='test_token', user_id=1)
        user_with_token = {'user': user, 'token': token}
        args = {'hackathon_name': 'test_hackathon_name'}

        with mock.patch('hackathon.user.user_mgr.UserManager.get_user_detail_info') as get_user_detail_info:
            detail = {'details': "details"}
            get_user_detail_info.return_value = detail
            with mock.patch('hackathon.hack.HackathonManager.get_hackathon_by_name') as get_hackathon_by_name:
                hackathon = Hackathon(id=1, name='test_hackathon')
                get_hackathon_by_name.return_value = hackathon
                # get register by hid and uid returns None
                with mock.patch(
                        'hackathon.registration.register_mgr.RegisterManger.get_register_by_rid_or_uid_and_hid') as get_register_by_rid_or_uid_and_hid:
                    get_register_by_rid_or_uid_and_hid.return_value = None
                    #Then get register by emails and hid returns None
                    with mock.patch(
                            'hackathon.registration.register_mgr.RegisterManger.get_register_by_emails_and_hid') as get_register_by_emails_and_hid:
                        get_register_by_emails_and_hid.return_value = None
                        with mock.patch(
                                'hackathon.registration.register_mgr.RegisterManger.deal_with_user_and_register_when_login') as deal_with_user_and_register_when_login:
                            deal_with_user_and_register_when_login.return_value = None

                            result = {}
                            detail['token'] = 'test_token'
                            result['user'] = detail
                            result['hackathon'] = hackathon.dic()
                            result['registration'] = {}

                            self.assertEqual(LoginProviderBase().return_details(user_with_token, args), result)
                            get_user_detail_info.assert_called_once_with(user)
                            get_hackathon_by_name.assert_called_once_with('test_hackathon_name')
                            get_register_by_rid_or_uid_and_hid.assert_called_once_with({'hid': 1, 'uid': 1})
                            get_register_by_emails_and_hid.assert_called_once_with(1, ANY)
                            deal_with_user_and_register_when_login.assert_called_once_with(user, 1)


    '''Test methnd provider login : QQ GitHub GitCafe Weibo'''

    def test_qq_login(self):
        user_manager = Mock()

        user = 'test_user'
        token = TestToken()
        user_with_token = {'user': user, 'token': token}
        user_manager.db_login.return_value = user_with_token

        detail = {'detail': 'test_detail'}
        user_manager.get_user_detail_info.return_value = detail

        args = {'access_token': 'test', 'hackathon_name': 'test'}

        with mock.patch('hackathon.user.login.get_remote') as get_remote_method:
            info = '''1234567890{"openid":"test_openid","client_id":"test_client_id"}1234'''
            email_info_resp = '''{"nickname":"test_nickname","figureurl":"test_figureurl"}'''
            get_remote_method.side_effect = [info, email_info_resp]

            with mock.patch('hackathon.user.login.QQLogin.return_details') as return_details:
                result = {'detail': 'test_detail', 'token': 'test_token'}
                return_details.return_value = result
                self.assertEqual(QQLogin(user_manager).login(args), result)
                self.assertEqual(user_manager.db_login.call_count, 1)
                self.assertEqual(get_remote_method.call_count, 2)

    def test_github_login(self):
        user_manager = Mock()

        user = 'test_user'
        token = TestToken()
        user_with_token = {'user': user, 'token': token}
        user_manager.db_login.return_value = user_with_token

        detail = {'detail': 'test_detail'}
        user_manager.get_user_detail_info.return_value = detail

        args = {'access_token': 'test', 'hackathon_name': 'test'}

        with mock.patch('hackathon.user.login.get_remote') as get_remote_method:
            user_info_resp = '''{"login":"test_login","name":"test_name","id":123456,"avatar_url":"http://test.com/test"}'''
            email_info_resp = '''{"email":"test@test.com"}'''
            get_remote_method.side_effect = [user_info_resp, email_info_resp]

            with mock.patch('hackathon.user.login.GithubLogin.return_details') as return_details:
                result = {'detail': 'test_detail', 'token': 'test_token'}
                return_details.return_value = result
                self.assertEqual(GithubLogin(user_manager).login(args), result)
                self.assertEqual(user_manager.db_login.call_count, 1)
                self.assertEqual(get_remote_method.call_count, 2)

    def test_gitcafe_login(self):
        user_manager = Mock()
        user = 'test_user'
        token = TestToken()
        user_with_token = {'user': user, 'token': token}
        user_manager.db_login.return_value = user_with_token

        detail = {'detail': 'test_detail'}
        user_manager.get_user_detail_info.return_value = detail

        args = {'access_token': 'test', 'hackathon_name': 'test'}

        with mock.patch('hackathon.user.login.get_remote') as get_remote_method:
            user_info_resp = '''{"email":"test@test.com","username":"test_name","fullname":"test_fullname","id":123456,"avatar_url":"https://test.com/test"}'''
            get_remote_method.return_value = user_info_resp

            with mock.patch('hackathon.user.login.GitcafeLogin.return_details') as return_details:
                result = {'detail': 'test_detail', 'token': 'test_token'}
                return_details.return_value = result
                self.assertEqual(GitcafeLogin(user_manager).login(args), result)
                self.assertEqual(user_manager.db_login.call_count, 1)
                self.assertEqual(get_remote_method.call_count, 1)

    def test_weibo_login(self):
        user_manager = Mock()

        user = 'test_user'
        token = TestToken()
        user_with_token = {'user': user, 'token': token}
        user_manager.db_login.return_value = user_with_token

        detail = {'detail': 'test_detail'}
        user_manager.get_user_detail_info.return_value = detail

        args = {'access_token': 'test', 'hackathon_name': 'test', 'uid': 'test_uid'}

        with mock.patch('hackathon.user.login.get_remote') as get_remote_method:
            user_info_resp = '''{"name":"test_name","screen_name":"test_screen_name","id":123456,"avatar_hd":"http://test.com/test"}'''
            email_info_resp = '''{"email":"test@test.com"}'''
            get_remote_method.side_effect = [user_info_resp, email_info_resp]

            with mock.patch('hackathon.user.login.WeiboLogin.return_details') as return_details:
                result = {'detail': 'test_detail', 'token': 'test_token'}
                return_details.return_value = result
                self.assertEqual(WeiboLogin(user_manager).login(args), result)
                self.assertEqual(user_manager.db_login.call_count, 1)
                self.assertEqual(get_remote_method.call_count, 2)