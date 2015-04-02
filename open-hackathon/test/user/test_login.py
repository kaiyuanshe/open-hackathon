import sys

sys.path.append("../src/hackathon")
import unittest
from hackathon.user.login import GithubLogin, QQLogin, WeiboLogin, GitcafeLogin
from hackathon import app
from mock import Mock
import mock


class TestToken:
    token = 'test_token'


class UserLoginTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def tearDown(self):
        pass


    def test_qq_login(self):
        user_manager = Mock()

        user = 'test_user'
        token = TestToken()
        user_with_token = {'user': user, 'token': token}
        user_manager.db_login.return_value = user_with_token

        detail = {'detail': 'test_detail'}
        user_manager.get_user_detail_info.return_value = detail

        result = {'detail': 'test_detail', 'token': 'test_token'}
        args = {'access_token': 'test', 'hackathon_name': 'test'}

        with mock.patch('hackathon.user.login.get_remote') as get_remote_method:
            info = '''1234567890{"openid":"test_openid","client_id":"test_client_id"}1234'''
            email_info_resp = '''{"nickname":"test_nickname","figureurl":"test_figureurl"}'''
            get_remote_method.side_effect = [info, email_info_resp]

            self.assertEqual(QQLogin(user_manager).login(args), result)
            self.assertEqual(user_manager.get_user_detail_info.call_count, 1)
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

        result = {'detail': 'test_detail', 'token': 'test_token'}
        args = {'access_token': 'test', 'hackathon_name': 'test'}

        with mock.patch('hackathon.user.login.get_remote') as get_remote_method:
            user_info_resp = '''{"login":"test_login","name":"test_name","id":123456,"avatar_url":"http://test.com/test"}'''
            email_info_resp = '''{"email":"test@test.com"}'''
            get_remote_method.side_effect = [user_info_resp, email_info_resp]

            self.assertEqual(GithubLogin(user_manager).login(args), result)
            self.assertEqual(user_manager.get_user_detail_info.call_count, 1)
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

        result = {'detail': 'test_detail', 'token': 'test_token'}
        args = {'access_token': 'test', 'hackathon_name': 'test'}

        with mock.patch('hackathon.user.login.get_remote') as get_remote_method:
            user_info_resp = '''{"email":"test@test.com","username":"test_name","fullname":"test_fullname","id":123456,"avatar_url":"https://test.com/test"}'''
            get_remote_method.return_value = user_info_resp

            self.assertEqual(GitcafeLogin(user_manager).login(args), result)
            self.assertEqual(user_manager.get_user_detail_info.call_count, 1)
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

        result = {'detail': 'test_detail', 'token': 'test_token'}
        args = {'access_token': 'test', 'hackathon_name': 'test', 'uid': 'test_uid'}

        with mock.patch('hackathon.user.login.get_remote') as get_remote_method:
            user_info_resp = '''{"name":"test_name","screen_name":"test_screen_name","id":123456,"avatar_hd":"http://test.com/test"}'''
            email_info_resp = '''{"email":"test@test.com"}'''
            get_remote_method.side_effect = [user_info_resp, email_info_resp]

            self.assertEqual(WeiboLogin(user_manager).login(args), result)
            self.assertEqual(user_manager.get_user_detail_info.call_count, 1)
            self.assertEqual(user_manager.db_login.call_count, 1)
            self.assertEqual(get_remote_method.call_count, 2)
