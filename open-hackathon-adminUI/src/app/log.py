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

import logging
import logging.config
from os.path import realpath, dirname
from logging import DEBUG, INFO


class Log(object):
    def __init__(self):
        logging.config.fileConfig("%s/logging.conf" % dirname(realpath(__file__)))
        # create logger
        self.logger = logging.getLogger("myLogger")

    def debug(self, debug):
        if self.logger.isEnabledFor(DEBUG):
            self.logger.debug(debug)

    def info(self, info):
        if self.logger.isEnabledFor(INFO):
            self.logger.info(info)

    def warn(self, warn):
        self.logger.warn(warn)

    def error(self, error):
        self.logger.error(str(error), exc_info=1)

    def critical(self, critical):
        self.logger.critical(critical)

# usage(make sure /var/log/openhackathon/ directory exists and accessible):
# from log import log
# log.info("some info")
log = Log()