import logging

file = "/home/kehl/workspace/OSSLab/webpy.log"
logformat = "[%(asctime)s] %(filename)s:%(lineno)d(%(funcName)s): [%(levelname)s] %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
loglevel = logging.DEBUG
interval = "d" 
backups = 3