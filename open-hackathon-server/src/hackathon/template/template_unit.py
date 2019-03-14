# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""


class TemplateUnit(object):
    """Unit of TemplateContent.

    An unit is a dict too that includes arguments for docker container or azure VM.
    Each unit represents a virtual_environment that can be started or stopped independently"""

    def __init__(self, provider):
        """Construct an new unit

        provider should be value of enum VE_PROVIDER.
        """
        self.provider = provider

    def get_name(self):
        raise NotImplemented

    def get_type(self):
        raise NotImplemented

    def get_description(self):
        raise NotImplemented
