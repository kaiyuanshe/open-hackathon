from . import ApiTestCase

from hackathon.constants import HACK_NOTICE_EVENT



class TestAdminApi(ApiTestCase):
    def test_create_hackathon(self, user1):
        self.login(user1)
        payload = self.client.post("/api/admin/hackathon")

    def test_update_hackathon(self, user1):
        self.login(user1)
        data = {}
        payload = self.client.put("/api/admin/hackathon", json_data=data)

    def test_online_offline_hackathon(self):
        self.login(user1)
        data = HACK_NOTICE_EVENT()
        payload_online = self.client.post("/api/admin/hackathon/online", json_data=data)
        payload_offline = self.client.post("/api/admin/hackathon/offline", json_data=data)

    def test_update_hackathon_config(self):
        pass

    def test_update_hackathon_organizers(self):
        pass

    def test_list_hackathon_admin(self):
        self.client.get("/api/hackathon/list")
        # pass

    def test_add_hackathon_admin(self):
        pass

    def test_delete_hackathon_admin(self):
        pass

    def test_get_team_score(self):
        pass

    def test_get_team_award(self):
        pass

    def test_get_hackathon_award(self):
        pass

    def test_list_user(self):
        self.client.get("/api/user/show/list")

    def test_list_host_server(self):
        pass

    def test_create_host_server(self):
        pass

    def test_update_host_server(self):
        pass

    def test_delete_host_server(self):
        pass

    def test_get_host_server(self):
        pass

    def test_create_hackathon_notice(self):
        pass

    def test_update_hackathon_notice(self):
        pass

    def test_delete_hackathon_notice(self):
        pass

    def test_get_hackathon_notice(self):
        pass
