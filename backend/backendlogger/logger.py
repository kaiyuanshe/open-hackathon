from wsgilog import WsgiLog
import constants

class Logger(WsgiLog):
    def __init__(self,application):
        WsgiLog.__init__(self,application,
                         logformat = constants.log_format,
                         tofile = True,
                         file = constants.log_file,
                         interval = constants.log_interval,
                         backups = constants.log_backups
                         )
