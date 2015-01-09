import logging
import logging.config
from os.path import realpath, dirname
from logging.handlers import RotatingFileHandler
from hackathon import app

#"application" code
class Log(object):
    def __init__(self):
        # logging.config.fileConfig("%s/logging.conf" % dirname(realpath(__file__)))
        loggers = [app.logger, logging.getLogger('sqlalchemy')]
        file_handler = RotatingFileHandler('/var/log/osslab/openhackathon.log', maxBytes=1024 * 1024 * 50, backupCount=14)
        file_handler.setLevel(logging.DEBUG)
        for logger in loggers:
            logger.addHandler(file_handler)

        self.logger = app.logger


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