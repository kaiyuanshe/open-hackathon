# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import logging
from os.path import realpath, dirname
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
        logging.config.fileConfig("%s/logging.conf" % dirname(realpath(__file__)))
        self.logger = logging.getLogger("hackathon_server")


log = Log()
