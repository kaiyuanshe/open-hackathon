from wsgilog import WsgiLog
import config

class Logger(WsgiLog):
    def __init__(self,application):
        WsgiLog.__init__(self,application,
                         logformat = config.logformat,
                         tofile = True,
                         file = config.file,
                         interval = config.interval,
                         backups = config.backups
                         )