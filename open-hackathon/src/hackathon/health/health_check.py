import sys

sys.path.append("..")
from hackathon.database.models import *
from hackathon.database import db_adapter
from hackathon.constants import HEALTH_STATE
from hackathon.docker import *

STATUS = "status"
DESCRIPTION = "description"


class HealthCheck():
    def reportHealth(self):
        pass


class MySQLHealthCheck(HealthCheck):

    def __init__(self):
        self.db = db_adapter

    def reportHealth(self):
        try:
            self.db.count(User)
            return {
                STATUS: HEALTH_STATE.OK
            }
        except Exception as e:
            return {
                STATUS: HEALTH_STATE.ERROR,
                DESCRIPTION: e.message
            }


class DockerHealthCheck(HealthCheck):

    def __init__(self):
        self.db = db_adapter
        self.docker = OssDocker()

    def reportHealth(self):
        try:
            hosts = self.db.find_all_objects(DockerHostServer)
            alive = 0
            for host in hosts:
                if self.docker.ping(host):
                    alive += 1
            if alive == len(hosts):
                return {
                    STATUS: HEALTH_STATE.OK
                }
            elif alive > 0:
                return {
                    STATUS: HEALTH_STATE.WARNING,
                    DESCRIPTION: 'at least one docker host servers are down'
                }
            else:
                return {
                    STATUS: HEALTH_STATE.ERROR,
                    DESCRIPTION: 'all docker host servers are down'
                }
        except Exception as e:
            return {
                STATUS: HEALTH_STATE.ERROR,
                "description": e.message
            }


class GuacamoleHealthCheck(HealthCheck):
    def reportHealth(self):
        # todo connect to guacamole to check its status. Maybe telnet?
        return {
            STATUS: HEALTH_STATE.OK
        }


class AzureHealthCheck(HealthCheck):
    def reportHealth(self):
        # todo connect to azure to check its status.
        return {
            STATUS: HEALTH_STATE.OK
        }
