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
from os.path import realpath, dirname, join
from logging import config, DEBUG, INFO

__all__ = ["log"]


class Log(object):
    """Wrapper of Python logging module for easier usage

    :Example:
        from hackathon.log import log

        log.info("message of INFO level ")
        log.error(exception) # where exception is of type Exception or it inheritances

    .. notes:: make sure directory '/var/log/open-hackathon/' exists and accessible
    """

    def debug(self, debug):
        """write message into log file with DEBUG level

        :type debug: str|unicode
        :param debug: message to write
        """
        if self.logger.isEnabledFor(DEBUG):
            self.logger.debug(debug)

    def info(self, info):
        """write message into log file with INFO level

        :type info: str|unicode
        :param info: message to write
        """
        if self.logger.isEnabledFor(INFO):
            self.logger.info(info)

    def warn(self, warn):
        """write message into log file with WARN level

        :type warn: str|unicode
        :param warn: message to write
        """
        self.logger.warn(warn)

    def error(self, exception):
        """write exception message and stack trace into log file with ERROR level

        :type exception: Exception
        :param exception: exception to write
        """
        self.logger.error(str(exception), exc_info=1)

    def critical(self, critical):
        """write message into log file with FATAL level

        :type critical: str|unicode
        :param critical: message to write
        """
        self.logger.critical(critical)

    def __init__(self):
        """initialize the log wrapper through 'logging.conf' file which should be in the same dir of this file"""
        logging.config.fileConfig(join(dirname(realpath(__file__)), "logging.conf"))
        self.logger = logging.getLogger("myLogger")


log = Log()
