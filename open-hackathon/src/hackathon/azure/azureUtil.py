__author__ = 'Yifu Huang'

from src.app.database import *
from src.app.log import *
import time
import os
import json

# resource name
STORAGE_ACCOUNT = 'storage account'
CLOUD_SERVICE = 'cloud service'
VIRTUAL_MACHINES = 'virtual machines'
DEPLOYMENT = 'deployment'
VIRTUAL_MACHINE = 'virtual machine'
# resource status
RUNNING = 'Running'
STOPPED = 'Stopped'
READY_ROLE = 'ReadyRole'
STOPPED_VM = 'StoppedVM'
STOPPED_DEALLOCATED = 'StoppedDeallocated'
# operation name
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
# operation status
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


def user_operation_commit(user_template, operation, status, note=None):
    """
    Commit user operation to database
    :param operation:
    :param status:
    :param note:
    :return:
    """
    user_operation = UserOperation(user_template, operation, status, note)
    db.session.add(user_operation)
    db.session.commit()


def user_resource_commit(user_template, type, name, status, cs_id=None):
    """
    Commit user resource to database
    :param type:
    :param name:
    :param status:
    :return:
    """
    user_resource = UserResource(user_template, type, name, status, cs_id)
    db.session.add(user_resource)
    db.session.commit()


def user_resource_status_update(user_template, type, name, status, cs_id=None):
    ur = UserResource.query.filter_by(user_template=user_template,
                                      type=type,
                                      name=name,
                                      cloud_service_id=cs_id).first()
    ur.status = status
    db.session.commit()


def vm_endpoint_commit(name, protocol, port, local_port, cs):
    """
    Commit vm endpoint to database before create vm
    :param name:
    :param protocol:
    :param port:
    :param local_port:
    :param cs:
    :return:
    """
    vm_endpoint = VMEndpoint(name, protocol, port, local_port, cs)
    db.session.add(vm_endpoint)
    db.session.commit()


def vm_endpoint_rollback(cs):
    """
    Rollback vm endpoint in database because no vm created
    :param cs:
    :return:
    """
    VMEndpoint.query.filter_by(cloud_service=cs, virtual_machine=None).delete()
    db.session.commit()


def vm_endpoint_update(cs, vm):
    """
    Update vm endpoint in database after vm created
    :param cs:
    :param vm:
    :return:
    """
    vm_endpoints = VMEndpoint.query.filter_by(cloud_service=cs, virtual_machine=None).all()
    for vm_endpoint in vm_endpoints:
        vm_endpoint.virtual_machine = vm
    db.session.commit()


def vm_config_commit(vm, dns, public_ip, private_ip):
    """
    Commit vm config to database
    :param vm:
    :return:
    """
    vm_config = VMConfig(vm, dns, public_ip, private_ip)
    db.session.add(vm_config)
    db.session.commit()


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
            log.debug('Timed out waiting for async operation to complete.')
            return False
        time.sleep(second_per_loop)
        result = sms.get_operation_status(request_id)
    if result.status != SUCCEEDED:
        log.debug(vars(result))
        if result.error:
            log.debug(result.error.code)
            log.debug(vars(result.error))
        log.debug('Asynchronous operation did not succeed.')
        return False
    return True


def load_template(user_template, operation):
    """
    Load json based template into dictionary
    :param user_template:
    :return:
    """
    # make sure template url exists
    if os.path.isfile(user_template.template.url):
        try:
            raw_template = json.load(file(user_template.template.url))
        except Exception as e:
            m = 'ugly json format: %s' % e.message
            user_operation_commit(user_template, operation, FAIL, m)
            log.debug(e)
            return None
    else:
        m = '%s not exist' % user_template.template.url
        user_operation_commit(user_template, operation, FAIL, m)
        log.debug(m)
        return None
    template_config = {T_EXPR_NAME: raw_template[T_EXPR_NAME],
                       T_STORAGE_ACCOUNT: raw_template[T_STORAGE_ACCOUNT],
                       T_CONTAINER: raw_template[T_CONTAINER],
                       T_CLOUD_SERVICE: raw_template[T_CLOUD_SERVICE],
                       T_DEPLOYMENT: raw_template[T_DEPLOYMENT],
                       T_VIRTUAL_MACHINES: raw_template[R_VIRTUAL_ENVIRONMENTS]}
    return template_config


def query_user_operation(user_template, operation):
    return UserOperation.query.filter_by(user_template=user_template). \
        filter(UserOperation.operation.like(operation + '%')).all()


def query_user_resource(user_template):
    return UserResource.query.filter_by(user_template=user_template).all()


def operation_status(user_template, operation):
    if UserOperation.query.filter_by(user_template=user_template, status=FAIL). \
            filter(UserOperation.operation.like(operation + '%')).count() > 0:
        return FAIL
    if UserOperation.query.filter_by(user_template=user_template, operation=operation, status=END).count() > 0:
        return END
    return START
