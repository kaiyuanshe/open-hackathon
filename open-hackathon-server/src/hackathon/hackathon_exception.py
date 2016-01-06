# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 
The MIT License (MIT)
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


class HackathonException(Exception):
    """Base of open hackathon platform exceptions"""

    def __init__(self):
        pass


class AlaudaException(HackathonException):
    """Exception that indicates failure in http request to Alauda"""

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __repr__(self):
        return "Failure in http request to Alauda: [%s]%s" % (self.code, self.message)


class ConfigurationException(HackathonException):
    """Exception that indicates bad configuration(s) in config.py"""

    def __init__(self, *config_section):
        self.config_section = config_section

    def __repr__(self):
        return "Fail to read configuration from config.py: %r" % self.config_section
