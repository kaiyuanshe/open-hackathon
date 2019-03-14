# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")
from docker_expr_starter import DockerExprStarter
from hackathon import RequiredFeature


class AlaudaDockerStarter(DockerExprStarter):
    docker = RequiredFeature("alauda_docker_proxy")

    def _get_docker_proxy(self):
        return self.docker
