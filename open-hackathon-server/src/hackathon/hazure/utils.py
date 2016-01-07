# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__author__ = "rapidhere"
__all__ = ["get_network_config"]

from azure.servicemanagement import ConfigurationSet, ConfigurationSetInputEndpoint


def get_network_config(is_vm_image, network_config, assigned_endpoints, update):
    """A helper to generate network config from azure_template_unit's network config

    # NOTE: refactor: de-couple from azure_template unit

    Return None if image type is vm and not update
    Public endpoint should be assigned in real time
    """
    from hackathon.template.template_constants import AZURE_UNIT

    if is_vm_image and not update:
        return None

    nc = network_config

    network_config = ConfigurationSet()
    network_config.configuration_set_type = nc[AZURE_UNIT.NETWORK_CONFIG_CONFIGURATION_SET_TYPE]
    input_endpoints = nc[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS]
    # avoid duplicate endpoint under same cloud service
    endpoints = map(lambda i: i[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_LOCAL_PORT], input_endpoints)
    unassigned_endpoints = map(str, __find_unassigned_endpoints(endpoints, assigned_endpoints))
    map(lambda (i, u): i.update({AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_PORT: u}), zip(input_endpoints, unassigned_endpoints))

    for input_endpoint in input_endpoints:
        network_config.input_endpoints.input_endpoints.append(
            ConfigurationSetInputEndpoint(
                input_endpoint[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_NAME],
                input_endpoint[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_PROTOCOL],
                input_endpoint[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_PORT],
                input_endpoint[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_LOCAL_PORT]
            )
        )

    return network_config


def __find_unassigned_endpoints(endpoints, assigned_endpoints):
    """
    Return a list of unassigned endpoints
    :param endpoints: a list of int or str
    :param assigned_endpoints: a list of int or str
    :return: unassigned_endpoints: a list of int
    """
    endpoints = map(int, endpoints)
    assigned_endpoints = map(int, assigned_endpoints)
    unassigned_endpoints = []
    for endpoint in endpoints:
        while endpoint in assigned_endpoints:
            endpoint = (endpoint + 1) % 65536
        assigned_endpoints.append(endpoint)
        unassigned_endpoints.append(endpoint)
    return unassigned_endpoints
