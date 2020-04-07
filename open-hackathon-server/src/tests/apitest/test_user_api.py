from . import ApiTestCase

from hackathon.constants import HACK_NOTICE_EVENT, HACK_NOTICE_CATEGORY
from hackathon.hmongo.models import HackathonNotice

USER_ONE_USERNAME = "test_one"
USER_ONE_ENCODE_PASSWORD = "0b92d6bab65b9b4cbd746a3effc516a7"


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

    def test_logout(self, user1):
        # do login
        self.login(user1)

        # get user profile
        payload = self.client.get("/api/user/profile")
        assert payload["id"] == str(user1.id)

        # do logout
        payload = self.client.delete("/api/user/login")
        assert payload['code'] == 200

        # get user profile failed
        payload = self.client.get("/api/user/profile")
        assert "error" in payload and payload["error"]["code"] == 401


class TestUserInfoApi(ApiTestCase):

    def test_get_user_profile(self, user1):
        self.login(user1)
        payload = self.client.get("/api/user/profile")
        assert payload["id"] == str(user1.id)

    def test_update_user_picture(self, user1):
        self.login(user1)
        data = {"url": "http://www.new-url.com/pic.jpg"}
        payload = self.client.put("/api/user/picture", json_data=data)
        # fixme api response is too arbitrary
        assert payload

    def test_read_user_notice(self, user1):
        self.login(user1)

        # init new unread msg
        hackathon_notice = HackathonNotice(
            content='',
            link='',
            event=HACK_NOTICE_EVENT.HACK_CREATE,
            category=HACK_NOTICE_CATEGORY.HACKATHON,
            receiver=user1,
            creator=user1,
        )
        hackathon_notice.save()
        assert not hackathon_notice.is_read

        # test read msg
        payload = self.client.put("/api/user/notice/read", json_data=dict(id=str(hackathon_notice.id)))
        assert payload['code'] == 200
        hackathon_notice = HackathonNotice.objects(id=str(hackathon_notice.id)).first()
        assert hackathon_notice.is_read


class TestUserFile(ApiTestCase):

    def test_user_upload_files(self):
        # TODO test for upload files
        pass


class TestTalents(ApiTestCase):

    def test_get_talents(self, user1):
        payload = self.client.get("/api/talent/list")
        assert len(payload) == 1 and payload[0]['id'] == str(user1.id)
