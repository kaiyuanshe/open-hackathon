# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""


class TemplateUnit(object):
    """Unit of TemplateContent.

    Each unit represents a virtual_environment that can be started or stopped independently"""

    def __init__(self, provider):
        """Construct an new unit

        provider should be value of enum VE_PROVIDER.
        """
        self.provider = provider

    def gen_k8s_yaml(self, expr_name):
        raise NotImplemented
