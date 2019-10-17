# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

__author__ = "rapidhere"
__all__ = ["ServiceAdapter"]

from hackathon import Component


class ServiceAdapter(Component):
    """the abstract ServiceAdapter with proxy pattern

    this adapter delegate the method and properties to the inner proxy, so make
    the adpater has all functions that adaptee has
    """

    def __init__(self, service):
        self.service = service

    def __getattr__(self, name):
        return getattr(self.service, name)
