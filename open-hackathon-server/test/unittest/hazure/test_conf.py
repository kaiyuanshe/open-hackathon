# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

__author__ = "rapidhere"


import random


# the subscription id and pem file used in test
# you can replace the args with your config
subscription_id = "bc41bdcd-7387-483f-a929-488fa27616a0"
pem_url = "/home/rapid/tmp/azure-test.pem"
management_host = "management.core.chinacloudapi.cn"

# general data for all test cases
meanless_id = "-233"
meanless_name = "random-meanless-name-" + str(random.random())

# used for real test cases
azure_cloud_service_name_should_exist = "ot-service-test"
azure_cloud_service_to_create = {
    "name": "rapid-test",
    "label": "rapid-test",
    "location": "China East"}  # optional value is "China North"
