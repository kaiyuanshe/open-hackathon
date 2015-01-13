import sys

sys.path.append("..")
from azure.servicemanagement import *
from hackathon.functions import get_config

sub_id = get_config("azure/subscriptionId")
cert_path = get_config('azure/certPath')
service_host_base = get_config("azure/managementServiceHostBase")

azure = ServiceManagementService(sub_id, cert_path, service_host_base)
