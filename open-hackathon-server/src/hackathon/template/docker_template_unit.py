# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
from hackathon.template.template_constants import DOCKER_UNIT
from hackathon.template.template_unit import TemplateUnit
from hackathon.constants import VE_PROVIDER

__all__ = ["DockerTemplateUnit"]


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
        pass
