from . import ApiTestCase

from hackathon.hmongo.models import UserHackathon

ADMIN_ONE_USERNAME = "admin_one"
ADMIN_ONE_ENCODE_PASSWORD = '0b92d6bab65b9b4cbd746a3effc516a7'

class TestAdminApi(ApiTestCase):
    
    def test_login_admin(self, admin1):
        # test login by DB
        data = {
            "provider": "db",
            "username": ADMIN_ONE_USERNAME,
            "password": ADMIN_ONE_ENCODE_PASSWORD,
            "code": "test-only"
        }
        payload = self.client.post("/api/user/login", json_data=data)
        print(payload)
        user_info = payload['user']
        assert user_info['id'], admin1.id

        data = {
            "provider": "db",
            "username": "admin_one_not_found",
            "password": ADMIN_ONE_ENCODE_PASSWORD,
            "code": "test-only"
        }
        payload = self.client.post("/api/user/login", json_data=data)
        assert "error" in payload

    def test_logout(self, admin1):
        # do login
        self.login(admin1)

        # get user profile
        payload = self.client.get("/api/user/profile")
        assert payload["id"] == str(admin1.id)

        # do logout
        payload = self.client.delete("/api/user/login")
        assert payload['code'] == 200

        # get user profile failed
        payload = self.client.get("/api/user/profile")
        assert "error" in payload and payload["error"]["code"] == 401


    def test_create_hackathon(self, admin1):
        self.login(admin1)
        data = {

        }
        payload = self.client.post("/api/admin/hackathon", json_data=data)
        # pass

    def test_online_offline_hackathon(self, admin1):
        self.login(admin1)
        data = {}
        payload_online = self.client.post("/api/admin/hackathon/online", json_data=data)
        print("===========payload_online==========")
        print(payload_online)
        assert payload_online['code'] == 200

        payload_offline = self.client.post("/api/admin/hackathon/offline", json_data=data)
        print("==========payload_offline==========")
        print(payload_offline)
        assert payload_offline['code'] == 200
        
    
    def test_update_hackathon_config(self, admin1):
        self.login(admin1)

    def test_update_hackathon_organizers(self, admin1):
        self.login(admin1)
    
    def test_list_hackathon_admin(self, admin1):
        # self.login(admin1)
        # self.client.get("/api/admin/hackathon/adminstrator/list")
        pass

    def test_add_hackathon_admin(self, admin1):
        # # ok
        # self.login(admin1)
        # data = {
        #     "id": str(admin1.id),
        #     "role": 1,
        #     "remark": "test"
        # }
        # self.client.post('/api/admin/hackathon/adminstrator', json_data=data)
        # assert payload['code'] == 200
        pass

    def test_update_hackathon(self, admin1):
        # ok 
        self.login(admin1)
        print("=============admin.id============")
        print("=============admin.id============")
        print("=============admin.id============")
        print(admin1.id)
        data = {
            "id": str(admin1.id),
            "role": 1,
            "remark": "test"
        }
        payload = self.client.put("/api/admin/hackathon/adminstrator", json_data=data)
        assert payload['code'] == 200

    def test_delete_hackathon_admin(self, admin1):
        # ok
        self.login(admin1)
        data = {
            "id": str(admin1.id)
        }
        self.client.delete('/api/admin/hackathon/adminstrator', json_data=data)
        assert payload['code'] == 200
        pass

    def test_get_team_score(self, admin1):
        self.login(admin1)

    def test_get_team_award(self, admin1):
        self.login(admin1)

    def test_get_hackathon_award(self, admin1):
        self.login(admin1)

    def test_list_user(self, admin1):
        self.login(admin1)
        self.client.get("/api/user/show/list")

    def test_list_host_server(self, admin1):
        self.login(admin1)

    def test_create_host_server(self, admin1):
        self.login(admin1)

    def test_update_host_server(self, admin1):
        self.login(admin1)

    def test_delete_host_server(self, admin1):
        self.login(admin1)

    def test_get_host_server(self, admin1):
        self.login(admin1)

    def test_create_hackathon_notice(self, admin1):
        self.login(admin1)

    def test_update_hackathon_notice(self, admin1):
        self.login(admin1)

    def test_delete_hackathon_notice(self, admin1):
        self.login(admin1)

    def test_get_hackathon_notice(self, admin1):
        self.login(admin1)
