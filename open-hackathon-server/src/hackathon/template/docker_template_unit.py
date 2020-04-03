# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
from hackathon.template.template_constants import DOCKER_UNIT
from hackathon.template.template_unit import TemplateUnit
from hackathon.constants import VE_PROVIDER

__all__ = ["DockerTemplateUnit"]

DEPLOYMENT_TEMPLATE = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ohp-{{ expr_name }}
  labels:
    app.kubernetes.io/name: ohp-{{ expr_name }}
    app.kubernetes.io/managed-by: ohp
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: ohp-{{ expr_name }}
      app.kubernetes.io/managed-by: ohp
  template:
    metadata:
      labels:
        app.kubernetes.io/name: ohp-{{ expr_name }}
        app.kubernetes.io/managed-by: ohp
    spec:
      containers:
      - name: environment
        image: {{ image }}
"""

SERVICE_TEMPLATE = """
apiVersion: v1
kind: Service
metadata:
  name: ohp-{{ expr_name }}
spec:
  selector:
    app.kubernetes.io/name: ohp-{{ expr_name }}
    app.kubernetes.io/managed-by: ohp
  ports:
  {{ ports }}
  type: NodePort
"""

PORT_TEMPLATE = """
  - protocol: TCP
    name: {{ name }}
    port: {{ port }}
"""


class DockerTemplateUnit(TemplateUnit):
    """
    Smallest unit in docker template
    """

    def __init__(self, config):
        super(DockerTemplateUnit, self).__init__(VE_PROVIDER.DOCKER)

        self.image = DOCKER_UNIT.IMAGE
        net_configs = config.get(DOCKER_UNIT.NET_CONFIG, [])
        self.network_configs = [{
            DOCKER_UNIT.NET_NAME: cfg[DOCKER_UNIT.NET_NAME],
            DOCKER_UNIT.NET_PORT: cfg[DOCKER_UNIT.NET_PORT],
            DOCKER_UNIT.NET_PROTOCOL: cfg[DOCKER_UNIT.NET_PROTOCOL],
        } for cfg in net_configs]

    def gen_k8s_yaml(self, expr_name):
        ports = []
        for cfg in self.network_configs:
            ports.append(PORT_TEMPLATE.format(**cfg))
        svc = ""
        if ports:
            svc = SERVICE_TEMPLATE.format(expr_name=expr_name, ports="\n".join(ports))

        deploy = DEPLOYMENT_TEMPLATE.format(expr_name=expr_name, image=self.image)

        return "{}\n---\n{}\n".format(deploy, svc)
