import sys

sys.path.append("../../src")

import unittest
from app import decorators

class DecoratorsTest(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_role_required_super_admin_success(self):
        return

    def test_role_required_super_admin_fail(self):
        return

    def test_role_required_comman_admin_success(self):
        return

    def test_role_required_comman_admin_fail(self):
        return