import sys

sys.path.append("../src/app")

import unittest
from app.functions import get_config,safe_get_config

class FunctionsTest(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_get_config_key_missing(self):
        self.assertEqual(get_config('hackathon-api.endpoint_test'),None)


    def test_get_config_format_error(self):
        self.assertEqual(get_config('mysql.sql'),None)


    def test_get_config(self):
        self.assertEqual(get_config('login.session_minutes'),60)


    def test_safe_get_config_default(self):
        self.assertEqual(get_config('mysql.sql'),None)
        self.assertEqual(safe_get_config('mysql.sql','default'),'default')


    def test_safe_get_config_value(self):
        self.assertEqual(get_config('login.session_minutes'),60)
        self.assertEqual(safe_get_config('login.session_minutes',66666),60)