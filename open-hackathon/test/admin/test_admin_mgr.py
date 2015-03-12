import unittest
from mock import Mock
from hackathon.admin.admin_mgr import admin_manager


class mytest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


    @unittest.skip("cannot pass")
    def test_get_id_from_token(self):
        self.assertEqual(admin_manager.get_hackid_from_adminID(1), [1L, 2L], 'test failed')


if __name__ == '__main__':
    unittest.main()

