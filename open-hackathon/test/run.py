# run test in command line:
# python -m unittest discover -v simple_example
# python -m unittest discover -s project_directory -p 'test*.py'
# or:
# python run_test.py

import unittest
import sys
from os.path import realpath, dirname

__usage__ = '''
%prog      # Searches CWD
%prog DIR
'''


def show_detail(items):
    for i in items:
        print repr(i)


def show_test_result(result):
    print
    print "---- START OF TEST RESULTS"
    print result
    print
    print "Result::errors"
    print show_detail(result.errors)
    print
    print "Result::failures"
    print show_detail(result.failures)
    print
    print "Result::skipped"
    print show_detail(result.skipped)
    print
    print "Result::successful"
    print result.wasSuccessful()
    print
    print "Result::test-run"
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