from . import ApiTestCase

USER_ONE_USERNAME = "test_one"
USER_ONE_ENCODE_PASSWORD = "16ec1ebb01fe02ded9b7d5447d3dfc65"


class TestUserLoginApi(ApiTestCase):

    def test_login(self, user1):
        # test login by DB
        data = {
            "provider": "db",
            "username": USER_ONE_USERNAME,
            "password": USER_ONE_ENCODE_PASSWORD,
            "code": "test-only"
        }
        payload = self.client.post("/api/user/login", json_data=data)
        user_info = payload['user']
        assert user_info['id'], user1.id

        data = {
            "provider": "db",
            "username": "user_one_not_found",
            "password": USER_ONE_ENCODE_PASSWORD,
            "code": "test-only"
        }
        payload = self.client.post("/api/user/login", json_data=data)
        assert "error" in payload

        # todo add sso test when support authing

    def test_logout(self):
        pass


class TestUserInfoApi(ApiTestCase):

    def test_get_user_profile(self, user1):
        self.login(user1)
        payload = self.client.get("/api/user/profile")
        assert payload["id"] == str(user1.id)

    def test_get_user_picture(self, user1):
        pass

    def test_get_user_notice(self, user1):
        pass


class TestUserFile(ApiTestCase):

    def test_user_upload_files(self):
        pass


class TestTalents(ApiTestCase):

    def test_get_talents(self):
        pass
