import logging
import logging.config
 
logging.config.fileConfig("logging.conf")
 
#create logger
logger = logging.getLogger("myLogger")
 
#"application" code

logger.info("info")

def log_debug(debug):
    logger.debug(debug)
    
def log_info(info):
    logger.info(info)

def log_warn(warn):
    logger.warn(warn)

def log_error(error):
    logger.error(str(error))

def log_critical(critical):
    logger.critical(critical)    
    
