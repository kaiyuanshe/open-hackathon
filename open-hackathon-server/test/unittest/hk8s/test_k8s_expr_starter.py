# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import unittest
from mock import Mock

# setup import path
try:
    import hackathon  # noqa
except ImportError:
    import os
    import sys
    BASE_DIR = os.path.dirname(__file__)
    sys.path.append(os.path.realpath(os.path.join(BASE_DIR, "..", "..", "..", "src")))


from hackathon import Component, RequiredFeature, Context
from hackathon.expr.k8s_expr_starter import K8SExprStarter
from hackathon import Context
from . import test_k8s_conf

class K8SExprStarterTest(unittest.TestCase):
    def setUp(self):
        hackathon_manager = RequiredFeature("hackathon_manager")
        template_library = RequiredFeature("template_library")
        self.service = K8SExprStarter()

    #prerequisites:
    #1, mock a hackathon record in db
    #2, mock an experiment record in db

    #@unittest.skip("skip test_start_expr")
    def test_start_expr(self):
        #TODO: mock record in db
        ctx = Context(template = "test_template", user = "test_user", hackathon = "test_hackathon")
        self.assertTrue(self.service.start_expr(ctx))

