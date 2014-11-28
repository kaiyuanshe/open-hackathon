import logging
import logging.config
 

#"application" code
class Log(object):
    def __init__(self):
        logging.config.fileConfig("logging.conf")
        #create logger
        self.logger = logging.getLogger("myLogger")

    def debug(self, debug):
        self.logger.debug(debug)

    def info(self, info):
        self.logger.info(info)

    def warn(self, warn):
        self.logger.warn(warn)

    def error(self, error):
        self.logger.error(str(error))

    def critical(self, critical):
        self.logger.critical(critical)

# usage(make sure /var/log/osslab/ directory exists and accessible):
# from log import log
# log.info("some info")
log = Log()