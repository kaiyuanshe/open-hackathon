__author__ = 'Yifu Huang'

from hackathon.azureautodeploy.azureImpl import *
from hackathon.functions import *
import sys

if __name__ == "__main__":
    args = sys.argv[1:]
    azure = AzureImpl()
    sub_id = get_config("azure/subscriptionId")
    cert_path = get_config('azure/certPath')
    service_host_base = get_config("azure/managementServiceHostBase")
    if not azure.connect(sub_id, cert_path, service_host_base):
        sys.exit(-1)
    user_template = db_adapter.get_object(UserTemplate, int(args[0]))
    try:
        result = azure.create_sync(user_template, int(args[1]))
    except Exception as e:
        log.error(e)
        sys.exit(-1)
    if not result:
        sys.exit(-1)
