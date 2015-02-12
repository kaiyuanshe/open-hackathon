import logging
import logging.config
from os.path import realpath, dirname

# "application" code
class Log(object):
    def __init__(self):
        logging.config.fileConfig("%s/logging.conf" % dirname(realpath(__file__)))
        # create logger
        self.logger = logging.getLogger("myLogger")

    def debug(self, debug):
        self.logger.debug(debug)

    def info(self, info):
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