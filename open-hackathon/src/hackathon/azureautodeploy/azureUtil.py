__author__ = 'Yifu Huang'
import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../../")
sys.path.append("..")
from hackathon.database import *
from hackathon.database.models import *
from hackathon.log import *
import time
import os
import json

# resource name in table UserResource
STORAGE_ACCOUNT = 'storage account'
CLOUD_SERVICE = 'cloud service'
VIRTUAL_MACHINES = 'virtual machines'
DEPLOYMENT = 'deployment'
VIRTUAL_MACHINE = 'virtual machine'
# resource status in table UserResource
RUNNING = 'Running'
STOPPED = 'Stopped'
# resource status in program
READY_ROLE = 'ReadyRole'
STOPPED_VM = 'StoppedVM'
STOPPED_DEALLOCATED = 'StoppedDeallocated'
# operation name in table UserOperation
CREATE = 'create'
CREATE_STORAGE_ACCOUNT = CREATE + ' ' + STORAGE_ACCOUNT
CREATE_CLOUD_SERVICE = CREATE + ' ' + CLOUD_SERVICE
CREATE_VIRTUAL_MACHINES = CREATE + ' ' + VIRTUAL_MACHINES
CREATE_DEPLOYMENT = CREATE + ' ' + DEPLOYMENT
CREATE_VIRTUAL_MACHINE = CREATE + ' ' + VIRTUAL_MACHINE
UPDATE = 'update'
UPDATE_VIRTUAL_MACHINE = UPDATE + ' ' + VIRTUAL_MACHINE
DELETE = 'delete'
DELETE_DEPLOYMENT = DELETE + ' ' + DEPLOYMENT
DELETE_VIRTUAL_MACHINE = DELETE + ' ' + VIRTUAL_MACHINE
SHUTDOWN = 'shutdown'
SHUTDOWN_VIRTUAL_MACHINE = SHUTDOWN + ' ' + VIRTUAL_MACHINE
# operation status in table UserOperation
START = 'start'
FAIL = 'fail'
END = 'end'
# os family name
WINDOWS = 'Windows'
LINUX = 'Linux'
# async wait name
WAIT_FOR_ASYNC = 'wait for async'
# async wait constants
ASYNC_TICK = 30
ASYNC_LOOP = 60
DEPLOYMENT_TICK = 30
DEPLOYMENT_LOOP = 60
VIRTUAL_MACHINE_TICK = 30
VIRTUAL_MACHINE_LOOP = 60
# async wait status
IN_PROGRESS = 'InProgress'
SUCCEEDED = 'Succeeded'
# template name
T_EXPR_NAME = 'expr_name'
T_STORAGE_ACCOUNT = 'storage_account'
T_CONTAINER = 'container'
T_CLOUD_SERVICE = 'cloud_service'
T_DEPLOYMENT = 'deployment'
T_VIRTUAL_MACHINES = 'virtual_machines'
R_VIRTUAL_ENVIRONMENTS = 'virtual_environments'


def user_operation_commit(template, operation, status, note=None):
    """
    Commit user operation to database
    :param operation:
    :param status:
    :param note:
    :return:
    """
    db_adapter.add_object_kwargs(UserOperation,
                                 template=template,
                                 operation=operation,
                                 status=status,
                                 note=note)
    db_adapter.commit()


def user_resource_commit(template, type, name, status, cs_id=None):
    """
    Commit user resource to database
    :param type:
    :param name:
    :param status:
    :return:
    """
    db_adapter.add_object_kwargs(UserResource,
                                 template=template,
                                 type=type,
                                 name=name,
                                 status=status,
                                 cloud_service_id=cs_id)
    db_adapter.commit()


def user_resource_status_update(template, type, name, status, cs_id=None):
    ur = db_adapter.find_first_object_by(UserResource,
                                      template_id=template.id,
                                      type=type,
                                      name=name,
                                      cloud_service_id=cs_id)
    ur.status = status
    db_adapter.commit()


def vm_endpoint_commit(name, protocol, port, local_port, cs, vm):
    """
    Commit vm endpoint to database before create vm
    :param name:
    :param protocol:
    :param port:
    :param local_port:
    :param cs:
    :return:
    """
    db_adapter.add_object_kwargs(VMEndpoint,
                                 name=name,
                                 protocol=protocol,
                                 public_port=port,
                                 private_port=local_port,
                                 cloud_service=cs,
                                 virtual_machine=vm)
    db_adapter.commit()


def vm_config_commit(vm, dns, public_ip, private_ip, remote_provider, remote_paras, template):
    """
    Commit vm config to database
    :param vm:
    :return:
    """
    db_adapter.add_object_kwargs(VMConfig,
                                 virtual_machine=vm,
                                 dns=dns,
                                 public_ip=public_ip,
                                 private_ip=private_ip,
                                 remote_provider=remote_provider,
                                 remote_paras=remote_paras,
                                 template=template)
    db_adapter.commit()


def wait_for_async(sms, request_id, second_per_loop, loop):
    """
    Wait for async operation, up to second_per_loop * loop
    :param request_id:
    :return:
    """
    count = 0
    result = sms.get_operation_status(request_id)
    while result.status == IN_PROGRESS:
        log.debug('%s [%s] loop count [%d]' % (WAIT_FOR_ASYNC, request_id, count))
        count += 1
        if count > loop:
            log.error('Timed out waiting for async operation to complete.')
            return False
        time.sleep(second_per_loop)
        result = sms.get_operation_status(request_id)
    if result.status != SUCCEEDED:
        log.error(vars(result))
        if result.error:
            log.error(result.error.code)
            log.error(vars(result.error))
        log.error('Asynchronous operation did not succeed.')
        return False
    return True


def load_template(template, operation, expr_id):
    """
    Load json based template into dictionary
    :param template:
    :return:
    """
    # make sure template url exists
    if os.path.isfile(template.url):
        try:
            raw_template = json.load(file(template.url))
        except Exception as e:
            m = 'ugly json format: %s' % e.message
            user_operation_commit(operation, FAIL, m)
            log.error(e)
            return None
    else:
        m = '%s not exist' % template.url
        user_operation_commit(operation, FAIL, m)
        log.error(m)
        return None
    template_config = {
        T_EXPR_NAME: raw_template[T_EXPR_NAME],
        T_STORAGE_ACCOUNT: raw_template[T_STORAGE_ACCOUNT],
        T_CONTAINER: raw_template[T_CONTAINER],
        T_CLOUD_SERVICE: raw_template[T_CLOUD_SERVICE],
        T_DEPLOYMENT: raw_template[T_DEPLOYMENT],
        T_VIRTUAL_MACHINES: raw_template[R_VIRTUAL_ENVIRONMENTS]
    }
    for vm in template_config[T_VIRTUAL_MACHINES]:
        vm['role_name'] = '%s-%d' % (vm['role_name'], expr_id)
    return template_config


def query_user_operation(template, operation, id):
    return db_adapter.find_all_objects(UserOperation,
                             UserOperation.template == template,
                             UserOperation.operation.like(operation + '%'),
                             UserOperation.id > id)


def query_user_resource(template, id):
    return db_adapter.find_all_objects(UserResource,
                             UserResource.template == template,
                             UserResource.id > id)
