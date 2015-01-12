__author__ = 'root'
import database
import log
from ossdocker import *

class RollBack(object):
    def __init__(self):
        pass

    def resetStatus(self, name):
        docker = OssDocker()
