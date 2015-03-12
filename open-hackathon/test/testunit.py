# A sample for unittest
import unittest
import sys

sys.path.append('../src/hackathon')
from hackathon.functions import get_config

# the method will be tested
class FunctionsTestCases(unittest.TestCase):
    #initialize
    def setUp(self):
        self.key = 'guacamole.host'

    #clean up
    def tearDown(self):
        self.key = None

    #test case must begin with test
    def testGetConfig(self):
        self.assertEqual("http://localhost:8080", get_config(self.key), 'get_config method is not working correctly')


if __name__ == "__main__":
    unittest.main()