from unittest import TestCase

from hackathon.hmongo.database import drop_db, setup_db

from . import TestClient


class TestUserLoginApi(TestCase):

    def setUp(self):
        drop_db()
        setup_db()

        self.client = TestClient()

    def tearDown(self):
        drop_db()

    def test_login(self, user1):
        pass

    def test_logout(self):
        pass


class TestUserInfoApi(TestCase):
    def test_get_user_profile(self):
        pass

    def test_get_user_picture(self):
        pass

    def test_get_user_notice(self):
        pass


class TestUserFile(TestCase):
    def test_user_upload_files(self):
        pass


class TestTalents(TestCase):
    def test_get_talents(self):
        pass
