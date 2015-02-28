import sys

sys.path.append("..")
from hackathon.constants import HEALTH_STATE
from hackathon.docker import *
from hackathon.azureautodeploy.azureImpl import *
from hackathon.functions import *

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

    # todo now check only server status
    def __init__(self):
        self.guacamole_url = get_config("guacamole.host") + '/guacamole'

    def reportHealth(self):
        try:
            req = requests.get(self.guacamole_url)
            log.debug(req.status_code)
            if req.status_code == 200:
                return {
                    STATUS: HEALTH_STATE.OK
                }
        except Exception as e:
            log.error(e)
        return {
            STATUS: HEALTH_STATE.ERROR
        }


class AzureHealthCheck(HealthCheck):

    def __init__(self):
        self.azure = AzureImpl()
        sub_id = get_config("azure.subscriptionId")
        cert_path = get_config('azure.certPath')
        service_host_base = get_config("azure.managementServiceHostBase")
        self.azure.connect(sub_id, cert_path, service_host_base)

    def reportHealth(self):
        if self.azure.ping():
            return {
                STATUS: HEALTH_STATE.OK
            }
        else:
            return {
                STATUS: HEALTH_STATE.ERROR
            }

g = GuacamoleHealthCheck()
print g.reportHealth()