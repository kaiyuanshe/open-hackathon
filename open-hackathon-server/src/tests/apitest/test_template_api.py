from . import ApiTestCase


class TestTemplateApi(ApiTestCase):
    def test_create_template(self, user1):
        self.login(user1)
        data = {}
        payload = self.client.post("/api/template", json_data=data)

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
        payload = self.client.delete("/api/template")
