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
__all__ = ["get_network_config", "get_remote_parameters", "add_endpoint_to_network_config", "find_unassigned_endpoints"]

from azure.servicemanagement import ConfigurationSet, ConfigurationSetInputEndpoint
from hackathon.template.template_constants import AZURE_UNIT

# endpoint constants
ENDPOINT_PREFIX = 'AUTO-'
ENDPOINT_PROTOCOL = 'TCP'


def get_network_config(network_config, assigned_endpoints):
    """A helper to generate network config from azure_template_unit's network config

    decouple from azure_template_unit.get_network_config
    Public endpoint should be assigned in real time
    """

    nc = network_config

    network_config = ConfigurationSet()
    network_config.configuration_set_type = nc[AZURE_UNIT.NETWORK_CONFIG_CONFIGURATION_SET_TYPE]
    input_endpoints = nc[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS]
    # avoid duplicate endpoint under same cloud service
    endpoints = map(lambda i: i[AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_LOCAL_PORT], input_endpoints)
    unassigned_endpoints = map(str, find_unassigned_endpoints(endpoints, assigned_endpoints))
    map(lambda (i, u): i.update({AZURE_UNIT.NETWORK_CONFIG_INPUT_ENDPOINTS_PORT: u}),
        zip(input_endpoints, unassigned_endpoints))

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


def get_remote_parameters(system_config, remote, name, hostname, port):
    """A helper to generate remote parameter from azure_template_unit

    decouple from azure_template_unit.get_remote_paras
    """
    r = remote
    sc = system_config

    return {
        AZURE_UNIT.REMOTE_PARAMETER_NAME: name,
        AZURE_UNIT.REMOTE_PARAMETER_DISPLAY_NAME: r[AZURE_UNIT.REMOTE_INPUT_ENDPOINT_NAME],
        AZURE_UNIT.REMOTE_PARAMETER_HOST_NAME: hostname,
        AZURE_UNIT.REMOTE_PARAMETER_PROTOCOL: r[AZURE_UNIT.REMOTE_PROTOCOL],
        AZURE_UNIT.REMOTE_PARAMETER_PORT: port,
        AZURE_UNIT.REMOTE_PARAMETER_USER_NAME: sc[AZURE_UNIT.SYSTEM_CONFIG_USER_NAME],
        AZURE_UNIT.REMOTE_PARAMETER_PASSWORD: sc[AZURE_UNIT.SYSTEM_CONFIG_USER_PASSWORD],
    }


def find_unassigned_endpoints(endpoints, assigned_endpoints):
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


def add_endpoint_to_network_config(network_config, public_endpoints, private_endpoints):
    """
    Return a new network config
    :param network_config:
    :param public_endpoints: a list of int or str
    :param private_endpoints: a list of int or str
    :return:
    """
    endpoints = zip(map(str, public_endpoints), map(str, private_endpoints))
    new_network_config = ConfigurationSet()
    new_network_config.configuration_set_type = network_config.configuration_set_type
    if network_config.input_endpoints is not None:
        for input_endpoint in network_config.input_endpoints.input_endpoints:
            new_network_config.input_endpoints.input_endpoints.append(
                ConfigurationSetInputEndpoint(input_endpoint.name,
                                              input_endpoint.protocol,
                                              input_endpoint.port,
                                              input_endpoint.local_port)
            )
    for endpoint in endpoints:
        new_network_config.input_endpoints.input_endpoints.append(
            ConfigurationSetInputEndpoint(ENDPOINT_PREFIX + endpoint[0],
                                          ENDPOINT_PROTOCOL,
                                          endpoint[0],
                                          endpoint[1])
        )
    return new_network_config


def delete_endpoint_from_network_config(network_config, private_endpoints):
    """
    Return a new network config
    :param network_config:
    :param private_endpoints: a list of int or str
    :return:
    """
    private_endpoints = map(str, private_endpoints)
    new_network_config = ConfigurationSet()
    new_network_config.configuration_set_type = network_config.configuration_set_type
    if network_config.input_endpoints is not None:
        for input_endpoint in network_config.input_endpoints.input_endpoints:
            if input_endpoint.local_port not in private_endpoints:
                new_network_config.input_endpoints.input_endpoints.append(
                    ConfigurationSetInputEndpoint(input_endpoint.name,
                                                  input_endpoint.protocol,
                                                  input_endpoint.port,
                                                  input_endpoint.local_port)
                )
    return new_network_config
