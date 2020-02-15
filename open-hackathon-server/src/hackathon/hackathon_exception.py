# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""


class HackathonException(Exception):
    """Base of open hackathon platform exceptions"""

    def __init__(self):
        pass

class ConfigurationException(HackathonException):
    """Exception that indicates bad configuration(s) in config.py"""

    def __init__(self, *config_section):
        self.config_section = config_section

    def __repr__(self):
        return "Fail to read configuration from config.py: %r" % self.config_section
