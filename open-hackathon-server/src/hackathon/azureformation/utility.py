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
__author__ = 'Yifu Huang'

import sys

sys.path.append("..")
from hackathon.database import (
    db_adapter,
)
from hackathon.database.models import (
    AzureLog,
    AzureStorageAccount,
    AzureCloudService,
    AzureDeployment,
    AzureVirtualMachine,
    AzureEndpoint,
    VirtualEnvironment,
    Template,
    Experiment,
)
from hackathon.util import (
    load_template,
    call,
    get_now,
)

from hackathon.enum import (
    ALStatus,
    EStatus,
    ALOperation,
    VEStatus,
)
from azure.servicemanagement import (
    ConfigurationSet,
    ConfigurationSetInputEndpoint,
)
from datetime import (
    timedelta,
)
from hackathon import (
    RequiredFeature
)
# -------------------------------------------------- constants --------------------------------------------------#
# project name
AZURE_FORMATION = 'Azure Formation'
# async wait constants
ASYNC_TICK = 30
ASYNC_LOOP = 60
DEPLOYMENT_TICK = 30
DEPLOYMENT_LOOP = 60
VIRTUAL_MACHINE_TICK = 30
VIRTUAL_MACHINE_LOOP = 60
PORT_BOUND = 65536
# endpoint constants
ENDPOINT_PREFIX = 'AUTO-'
ENDPOINT_PROTOCOL = 'TCP'
# module base
MDL_BASE = 'hackathon.azureformation.'
# module name, class name and function name
MDL_CLS_FUNC = [
    [MDL_BASE + 'storageAccount', 'StorageAccount', 'create_storage_account'],
    [MDL_BASE + 'cloudService', 'CloudService', 'create_cloud_service'],
    [MDL_BASE + 'service', 'Service', 'query_async_operation_status'],
    [MDL_BASE + 'storageAccount', 'StorageAccount', 'create_storage_account_async_true'],
    [MDL_BASE + 'storageAccount', 'StorageAccount', 'create_storage_account_async_false'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine_async_true_1'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine_async_false_1'],
    [MDL_BASE + 'service', 'Service', 'query_virtual_machine_status'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine_vm_true_1'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine_async_true_2'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine_async_false_2'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine_vm_true_2'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine_async_true_3'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine_async_false_3'],
    [MDL_BASE + 'service', 'Service', 'query_deployment_status'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'create_virtual_machine_dm_true'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'stop_virtual_machine'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'stop_virtual_machine_async_true'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'stop_virtual_machine_async_false'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'stop_virtual_machine_vm_true'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'start_virtual_machine'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'start_virtual_machine_async_true'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'start_virtual_machine_async_false'],
    [MDL_BASE + 'virtualMachine', 'VirtualMachine', 'start_virtual_machine_vm_true'],
]
DEFAULT_TICK = 3


# -------------------------------------------------- azure log --------------------------------------------------#
def commit_azure_log(experiment_id, operation, status, note=None, code=None):
    db_adapter.add_object_kwargs(AzureLog,
                                 experiment_id=experiment_id,
                                 operation=operation,
                                 status=status,
                                 note=note,
                                 code=code)
    db_adapter.commit()
    if status == ALStatus.FAIL:
        update_experiment_status(experiment_id, EStatus.Failed)
    elif status == ALStatus.END:
        need_status = EStatus.Running
        if operation == ALOperation.STOP_VIRTUAL_MACHINE:
            need_status = EStatus.Stopped
        check_experiment_done(experiment_id, need_status)


# --------------------------------------------- azure storage account ---------------------------------------------#
def commit_azure_storage_account(name, description, label, location, status, experiment_id):
    db_adapter.add_object_kwargs(AzureStorageAccount,
                                 name=name,
                                 description=description,
                                 label=label,
                                 location=location,
                                 status=status,
                                 experiment_id=experiment_id)
    db_adapter.commit()


def contain_azure_storage_account(name):
    return db_adapter.count_by(AzureStorageAccount, name=name) != 0


def delete_azure_storage_account(name):
    db_adapter.delete_all_objects_by(AzureStorageAccount, name=name)
    db_adapter.commit()


# --------------------------------------------- azure cloud service ---------------------------------------------#
def commit_azure_cloud_service(name, label, location, status, experiment_id):
    db_adapter.add_object_kwargs(AzureCloudService,
                                 name=name,
                                 label=label,
                                 location=location,
                                 status=status,
                                 experiment_id=experiment_id)
    db_adapter.commit()


def contain_azure_cloud_service(name):
    return db_adapter.count_by(AzureCloudService, name=name) != 0


def delete_azure_cloud_service(name):
    db_adapter.delete_all_objects_by(AzureCloudService, name=name)
    db_adapter.commit()


# --------------------------------------------- azure deployment ---------------------------------------------#
def commit_azure_deployment(name, slot, status, cloud_service_name, experiment_id):
    cs = db_adapter.find_first_object_by(AzureCloudService, name=cloud_service_name)
    db_adapter.add_object_kwargs(AzureDeployment,
                                 name=name,
                                 slot=slot,
                                 status=status,
                                 cloud_service=cs,
                                 experiment_id=experiment_id)
    db_adapter.commit()


def contain_azure_deployment(cloud_service_name, deployment_slot):
    cs = db_adapter.find_first_object_by(AzureCloudService, name=cloud_service_name)
    return db_adapter.count_by(AzureDeployment,
                               slot=deployment_slot,
                               cloud_service_id=cs.id) != 0


def delete_azure_deployment(cloud_service_name, deployment_slot):
    cs = db_adapter.find_first_object_by(AzureCloudService, name=cloud_service_name)
    db_adapter.delete_all_objects_by(AzureDeployment,
                                     slot=deployment_slot,
                                     cloud_service_id=cs.id)
    db_adapter.commit()


# --------------------------------------------- azure virtual machine ---------------------------------------------#
def commit_azure_virtual_machine(name, label, status, dns, public_ip, private_ip,
                                 cloud_service_name, deployment_name, experiment_id, virtual_environment):
    cs = db_adapter.find_first_object_by(AzureCloudService, name=cloud_service_name)
    dm = db_adapter.find_first_object_by(AzureDeployment, name=deployment_name, cloud_service=cs)
    vm = db_adapter.add_object_kwargs(AzureVirtualMachine,
                                      name=name,
                                      label=label,
                                      status=status,
                                      dns=dns,
                                      public_ip=public_ip,
                                      private_ip=private_ip,
                                      deployment=dm,
                                      experiment_id=experiment_id,
                                      virtual_environment=virtual_environment)
    db_adapter.commit()
    return vm


def contain_azure_virtual_machine(cloud_service_name, deployment_name, virtual_machine_name):
    cs = db_adapter.find_first_object_by(AzureCloudService, name=cloud_service_name)
    dm = db_adapter.find_first_object_by(AzureDeployment, name=deployment_name, cloud_service=cs)
    return db_adapter.count_by(AzureVirtualMachine,
                               name=virtual_machine_name,
                               deployment_id=dm.id) != 0


def delete_azure_virtual_machine(cloud_service_name, deployment_name, virtual_machine_name):
    cs = db_adapter.find_first_object_by(AzureCloudService, name=cloud_service_name)
    dm = db_adapter.find_first_object_by(AzureDeployment, name=deployment_name, cloud_service=cs)
    db_adapter.delete_all_objects_by(AzureVirtualMachine,
                                     name=virtual_machine_name,
                                     deployment_id=dm.id)
    db_adapter.commit()


def get_azure_virtual_machine_status(cloud_service_name, deployment_name, virtual_machine_name):
    cs = db_adapter.find_first_object_by(AzureCloudService, name=cloud_service_name)
    dm = db_adapter.find_first_object_by(AzureDeployment, name=deployment_name, cloud_service=cs)
    vm = db_adapter.find_first_object_by(AzureVirtualMachine, name=virtual_machine_name, deployment=dm)
    return vm.status


def update_azure_virtual_machine_status(cloud_service_name, deployment_name, virtual_machine_name, status):
    cs = db_adapter.find_first_object_by(AzureCloudService, name=cloud_service_name)
    dm = db_adapter.find_first_object_by(AzureDeployment, name=deployment_name, cloud_service=cs)
    vm = db_adapter.find_first_object_by(AzureVirtualMachine, name=virtual_machine_name, deployment=dm)
    vm.status = status
    db_adapter.commit()
    return vm


def update_azure_virtual_machine_private_ip(virtual_machine, private_ip):
    virtual_machine.private_ip = private_ip
    db_adapter.commit()


def update_azure_virtual_machine_public_ip(virtual_machine, public_ip):
    virtual_machine.public_ip = public_ip
    db_adapter.commit()


# --------------------------------------------- azure endpoint ---------------------------------------------#
def commit_azure_endpoint(name, protocol, public_port, private_port, virtual_machine):
    db_adapter.add_object_kwargs(AzureEndpoint,
                                 name=name,
                                 protocol=protocol,
                                 public_port=public_port,
                                 private_port=private_port,
                                 virtual_machine=virtual_machine)
    db_adapter.commit()


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
            endpoint = (endpoint + 1) % PORT_BOUND
        assigned_endpoints.append(endpoint)
        unassigned_endpoints.append(endpoint)
    return unassigned_endpoints


# --------------------------------------------- virtual environment ---------------------------------------------#
def commit_virtual_environment(provider, name, image, status, remote_provider, remote_paras, experiment_id):
    ve = db_adapter.add_object_kwargs(VirtualEnvironment,
                                      provider=provider,
                                      name=name,
                                      image=image,
                                      status=status,
                                      remote_provider=remote_provider,
                                      remote_paras=remote_paras,
                                      experiment_id=experiment_id)
    db_adapter.commit()
    return ve


def update_virtual_environment_status(virtual_machine, status):
    ve = virtual_machine.virtual_environment
    ve.status = status
    db_adapter.commit()


def update_virtual_environment_remote_paras(virtual_machine, remote_paras):
    ve = virtual_machine.virtual_environment
    ve.remote_paras = remote_paras
    db_adapter.commit()


# --------------------------------------------- network config ---------------------------------------------#
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


# --------------------------------------------- template ---------------------------------------------#
def load_template_from_experiment(experiment_id):
    e = db_adapter.get_object(Experiment, experiment_id)
    t = db_adapter.get_object(Template, e.template_id)
    return load_template(t.url)


def set_template_virtual_environment_count(experiment_id, count):
    e = db_adapter.get_object(Experiment, experiment_id)
    t = db_adapter.get_object(Template, e.template_id)
    t.virtual_environment_count = count
    db_adapter.commit()


# --------------------------------------------- scheduler ---------------------------------------------#
def run_job(mdl_cls_func, cls_args, func_args, second=DEFAULT_TICK):
    exec_time = get_now() + timedelta(seconds=second)
    scheduler = RequiredFeature("scheduler")
    scheduler.get_scheduler().add_job(call, 'date', run_date=exec_time, args=[mdl_cls_func, cls_args, func_args])


# --------------------------------------------- experiment ---------------------------------------------#
def update_experiment_status(experiment_id, status):
    e = db_adapter.get_object(Experiment, experiment_id)
    e.status = status
    db_adapter.commit()


def check_experiment_done(experiment_id, need_status):
    e = db_adapter.get_object(Experiment, experiment_id)
    need_ve_status = VEStatus.Running
    if need_status == EStatus.Stopped:
        need_ve_status = VEStatus.Stopped
    if db_adapter.count_by(VirtualEnvironment,
                           experiment_id=experiment_id,
                           status=need_ve_status) == e.template.virtual_environment_count:
        update_experiment_status(experiment_id, need_status)