# this is daemon for unittest
import unittest
from open-hackathon.src.hackathon.functions.py import get_config

#the method will be tested
class FunctionsTestCases(unittest,Testcase):
    #initialize
    def setUp(self):
        pass
    #clean up
    def tearDown(self):
        pass
    #test case must begin with test
    def testGetConfig(self):
        self.assertEqual(self.get_config('azure.subscriptionId'),'7946a60d-67b1-43f0-96f9-1c558a9d284c')






if __name__ == "__main__":
    unittest.main()