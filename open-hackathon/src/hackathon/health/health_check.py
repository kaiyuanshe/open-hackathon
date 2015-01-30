import sys

sys.path.append("..")
from hackathon.database.models import User
from hackathon.database import db_adapter
from hackathon.constants import HEALTH_STATE

STATUS = "status"


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
                "description": e.message
            }


class DockerHealthCheck(HealthCheck):
    def reportHealth(self):
        # todo connect to docker host servers
        return {
            STATUS: HEALTH_STATE.OK
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
