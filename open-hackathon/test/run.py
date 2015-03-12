# run test in command line:
# python -m unittest discover -v simple_example
# python -m unittest discover -s project_directory -p 'test*.py'
# or:
# python run_test.py

import unittest
import sys
import os
from os.path import isfile, join, isdir, realpath, dirname

__usage__ = '''
%prog      # Searches CWD
%prog DIR
'''


def show_test_result(result):
    print
    print "---- START OF TEST RESULTS"
    print result
    print
    print "fooResult::errors"
    print result.errors
    print
    print "fooResult::failures"
    print result.failures
    print
    print "fooResult::skipped"
    print result.skipped
    print
    print "fooResult::successful"
    print result.wasSuccessful()
    print
    print "fooResult::test-run"
    print result.testsRun
    print "---- END OF TEST RESULTS"
    print


if __name__ == '__main__':
    if len(sys.argv) > 1:
        unit_dir = sys.argv[1]
    else:
        unit_dir = dirname(realpath(__file__))

    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().discover(unit_dir))
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(suite)
    show_test_result(test_result)