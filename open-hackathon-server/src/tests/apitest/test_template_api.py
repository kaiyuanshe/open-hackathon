from hackathon.constants import CLOUD_PROVIDER

from . import ApiTestCase


class TestTemplateApi(ApiTestCase):
    def test_create_template(self, user1):
        self.login(user1)

        # create with err content
        payload = self.client.post("/api/template", json_data={})
        assert "error" in payload and payload['error']['code'] == 400

        data = {
            "name": "test_create_template",
            "description": "中文测试",
            "virtual_environments": [{
                "provider": CLOUD_PROVIDER.KUBERNETES,
            }],
        }
        payload = self.client.post("/api/template", json_data=data)
        assert payload['name'] == 'test_create_template'

    def test_get_template_by_id(self, user1, default_template):
        self.login(user1)

    def test_update_template(self, user1, default_template):
        self.login(user1)

    def test_create_template_from_file(self, user1):
        self.login(user1)

    def test_list_templates(self, user1):
        self.login(user1)

    def test_delete_template(self, user1):
        self.login(user1)
