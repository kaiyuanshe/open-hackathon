from . import ApiTestCase

from hackathon.hmongo.models import UserHackathon

class TestAdminApi(ApiTestCase):
    def test_create_hackathon(self, admin1):
        self.login(admin1)
        data = {}
        payload = self.client.post("/api/admin/hackathon", json_data=data)

    def test_update_hackathon(self, admin1):
        # ok 
        self.login(admin1)
        data = {
            "id": str(admin1.id),
            "role": 1,
            "remark": "test"
        }
        payload = self.client.put("/api/admin/hackathon/adminstrator", json_data=data)
        assert payload['code'] == 200

    def test_online_offline_hackathon(self, admin1):
        self.login(admin1)
        data = {}
        payload_online = self.client.post("/api/admin/hackathon/online", json_data=data)
        payload_offline = self.client.post("/api/admin/hackathon/offline", json_data=data)

    def test_update_hackathon_config(self, admin1):
        self.login(admin1)

    def test_update_hackathon_organizers(self, admin1):
        self.login(admin1)

    def test_list_hackathon_admin(self, admin1):
        self.login(admin1)
        self.client.get("/api/admin/hackathon/adminstrator/list")

    def test_add_hackathon_admin(self, admin1):
        # ok
        self.login(admin1)
        data = {
            "id": str(admin1.id),
            "role": 1,
            "remark": "test"
        }
        self.client.post('/api/admin/hackathon/adminstrator', json_data=data)
        assert payload['code'] == 200

    def test_delete_hackathon_admin(self, admin1):
        # ok
        self.login(admin1)
        data = {
            "id": str(admin1.id)
        }
        self.client.delete('/api/admin/hackathon/adminstrator', json_data=data)
        assert payload['code'] == 200

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
