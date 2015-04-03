# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#  
# The MIT License (MIT)
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#  
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

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