# -*- coding: UTF-8 -*-
from hackathon.constants import VE_PROVIDER

from . import ApiTestCase

valid_k8s_yml_template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ expr_name }}-nginx-deployment
  labels:
    app: {{ expr_name }}-nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {{ expr_name }}-nginx
  template:
    metadata:
      labels:
        app: {{ expr_name }}-nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.7.9
        ports:
        - containerPort: 80
"""

invalid_k8s_yml_template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.7.9
        ports:
        - containerPort: 80
"""


class TestTemplateApi(ApiTestCase):
    def test_create_template_by_docker_image(self, user1):
        self.login(user1)

        data = {
            "name": "test_create_image_template",
            "description": "中文测试",
            "virtual_environment": {
                "provider": VE_PROVIDER.DOCKER,
                "image": "open-hackathon-server:test-only"
            },
        }
        payload = self.client.post("/api/template", json_data=data)
        assert payload['name'] == 'test_create_image_template'

    def test_create_template_by_yml_template(self):
        invalid_data = {
            "name": "test_create_k8s_template_failed",
            "description": "中文测试",
            "virtual_environment": {
                "provider": VE_PROVIDER.K8S,
                "yaml_template": invalid_k8s_yml_template,
            },
        }
        payload = self.client.post("/api/template", json_data=invalid_data)
        assert "error" in payload

        valid_data = {
            "name": "test_create_k8s_template",
            "description": "中文测试",
            "virtual_environment": {
                "provider": VE_PROVIDER.K8S,
                "yaml_template": valid_k8s_yml_template,
            },
        }
        payload = self.client.post("/api/template", json_data=valid_data)
        assert payload['name'] == 'test_create_k8s_template'

    def test_create_template_failed_case(self, user1):
        self.login(user1)

        # create with err content
        payload = self.client.post("/api/template", json_data={})
        assert "error" in payload and payload['error']['code'] == 400

    def test_get_template_by_id(self, user1, default_template):
        self.login(user1)

    def test_update_template(self, user1, default_template):
        self.login(user1)

    def test_list_templates(self, user1):
        self.login(user1)

    def test_delete_template(self, user1):
        self.login(user1)
