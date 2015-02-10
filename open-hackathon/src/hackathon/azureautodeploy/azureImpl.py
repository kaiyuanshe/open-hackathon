__author__ = 'Yifu Huang'
import sys

sys.path.append("..")
from azureStorage import *
from azureCloudService import *
from azureVirtualMachines import *
from azure.servicemanagement import *


class AzureImpl():
    """
    Azure cloud service management
    For logic: besides resources created by this program itself, it can reuse other storage,
    container, cloud service and deployment exist in azure (by sync them into database)
    For template: one storage account, one container, one cloud service, one deployment,
    multiple virtual machines (Windows/Linux), multiple input endpoints
    """

    def __init__(self):
        self.sms = None
        self.user_template = None
        self.template_config = None
        self.update_template_config = None

    def connect(self, subscription_id, pem_url, management_host):
        """
        Connect to azure service management service according to given user info
        :return: Whether service management service is connected
        """
        try:
            self.sms = ServiceManagementService(subscription_id, pem_url, management_host)
        except Exception as e:
            log.error(e)
            return False
        return True

    def ping(self):
        """
        Use list storage accounts to check azure service management service health
        :return:
        """
        try:
            self.sms.list_storage_accounts()
        except Exception as e:
            log.error(e)
            return False
        return True

    def create_sync(self, user_template, expr_id):
        """
        Create virtual machines according to given user template (assume all fields needed are in template)
        1. Load template from json into dictionary
        2. If storage account not exist, then create it
        3. If cloud service not exist, then create it
        4. If deployment not exist, then create virtual machine with deployment
           Else add virtual machine to deployment
        :param user_template:
        :return: Whether a virtual machines are created
        """
        self.user_template = user_template
        user_operation_commit(self.user_template, CREATE, START)
        self.template_config = load_template(user_template, CREATE, expr_id)
        if self.template_config is None:
            return False
        if not AzureStorage(self.sms, self.user_template, self.template_config).create_storage_account():
            return False
        if not AzureCloudService(self.sms, self.user_template, self.template_config).create_cloud_service():
            return False
        if not AzureVirtualMachines(self.sms, self.user_template, self.template_config).create_virtual_machines():
            return False
        user_operation_commit(self.user_template, CREATE, END)
        return True

    def shutdown_sync(self, user_template, expr_id):
        """
        Shutdown virtual machines according to given user template (assume all fields needed are in template)
        :param user_template:
        :return:
        """
        self.user_template = user_template
        user_operation_commit(self.user_template, SHUTDOWN, START)
        self.template_config = load_template(user_template, SHUTDOWN, expr_id)
        if self.template_config is None:
            return False
        cloud_service = self.template_config['cloud_service']
        deployment = self.template_config['deployment']
        virtual_machines = self.template_config['virtual_machines']
        cs = self.__resource_check(cloud_service, deployment, virtual_machines, SHUTDOWN)
        if cs is None:
            return False
        # now check done, begin
        for virtual_machine in virtual_machines:
            user_operation_commit(self.user_template, SHUTDOWN_VIRTUAL_MACHINE, START)
            try:
                result = self.sms.shutdown_role(cloud_service['service_name'],
                                                deployment['deployment_name'],
                                                virtual_machine['role_name'])
            except Exception as e:
                user_operation_commit(self.user_template, SHUTDOWN_VIRTUAL_MACHINE, FAIL, e.message)
                log.error(e)
                return False
            # make sure async operation succeeds
            if not wait_for_async(self.sms, result.request_id, ASYNC_TICK, ASYNC_LOOP):
                m = WAIT_FOR_ASYNC + ' ' + FAIL
                user_operation_commit(self.user_template, SHUTDOWN_VIRTUAL_MACHINE, FAIL, m)
                log.error(m)
                return False
            # make sure role is stopped
            if not AzureVirtualMachines(self.sms, self.user_template, self.template_config). \
                    wait_for_role(cloud_service['service_name'],
                                  deployment['deployment_name'],
                                  virtual_machine['role_name'],
                                  VIRTUAL_MACHINE_TICK,
                                  VIRTUAL_MACHINE_LOOP,
                                  STOPPED_VM):
                m = '%s %s shutdown but not ready' % (VIRTUAL_MACHINE, virtual_machine['role_name'])
                user_operation_commit(self.user_template, SHUTDOWN_VIRTUAL_MACHINE, FAIL, m)
                log.error(m)
                return False
            user_resource_status_update(self.user_template,
                                        VIRTUAL_MACHINE,
                                        virtual_machine['role_name'],
                                        STOPPED,
                                        cs.id)
            user_operation_commit(self.user_template, SHUTDOWN_VIRTUAL_MACHINE, END)
        user_operation_commit(self.user_template, SHUTDOWN, END)
        return True

    def delete_sync(self, user_template, expr_id):
        """
        Delete virtual machines according to given user template (assume all fields needed are in template)
        If deployment has only a virtual machine, then delete a virtual machine with deployment
        Else delete a virtual machine from deployment
        :param user_template:
        :return: Whether a virtual machine is deleted
        """
        self.user_template = user_template
        user_operation_commit(self.user_template, DELETE, START)
        self.template_config = load_template(user_template, DELETE, expr_id)
        if self.template_config is None:
            return False
        cloud_service = self.template_config['cloud_service']
        deployment = self.template_config['deployment']
        virtual_machines = self.template_config['virtual_machines']
        cs = self.__resource_check(cloud_service, deployment, virtual_machines, DELETE)
        if cs is None:
            return False
        # now check done, begin update
        for virtual_machine in virtual_machines:
            deploy = self.sms.get_deployment_by_slot(cloud_service['service_name'], deployment['deployment_slot'])
            # whether only one virtual machine in deployment
            if len(deploy.role_instance_list) == 1:
                user_operation_commit(self.user_template, DELETE_DEPLOYMENT, START)
                user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, START)
                try:
                    result = self.sms.delete_deployment(cloud_service['service_name'], deployment['deployment_name'])
                except Exception as e:
                    user_operation_commit(self.user_template, DELETE_DEPLOYMENT, FAIL, e.message)
                    user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, FAIL, e.message)
                    log.error(e)
                    return False
                # make sure async operation succeeds
                if not wait_for_async(self.sms, result.request_id, ASYNC_TICK, ASYNC_LOOP):
                    m = WAIT_FOR_ASYNC + ' ' + FAIL
                    user_operation_commit(self.user_template, DELETE_DEPLOYMENT, FAIL, m)
                    user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, FAIL, m)
                    log.error(m)
                    return False
                # make sure deployment not exist
                if AzureVirtualMachines(self.sms, self.user_template, self.template_config). \
                        deployment_exists(cloud_service['service_name'], deployment['deployment_slot']):
                    m = '%s %s deleted but failed' % (DEPLOYMENT, deployment['deployment_name'])
                    user_operation_commit(self.user_template, DELETE_DEPLOYMENT, FAIL, m)
                    log.error(m)
                    return False
                else:
                    # delete deployment
                    db_adapter.delete_all_objects(UserResource,
                                                  user_template_id=user_template.id,
                                                  type=DEPLOYMENT,
                                                  name=deployment['deployment_name'],
                                                  cloud_service_id=cs.id)
                    db_adapter.commit()
                    user_operation_commit(self.user_template, DELETE_DEPLOYMENT, END)
                # make sure virtual machine not exist
                if AzureVirtualMachines(self.sms, self.user_template, self.template_config). \
                        role_exists(cloud_service['service_name'],
                                    deployment['deployment_name'],
                                    virtual_machine['role_name']):
                    m = '%s %s deleted but failed' % (VIRTUAL_MACHINE, virtual_machine['role_name'])
                    user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, FAIL, m)
                    log.error(m)
                    return False
                else:
                    # delete vm, cascade delete vm endpoint and vm config
                    db_adapter.delete_all_objects(UserResource,
                                                  user_template_id=user_template.id,
                                                  type=VIRTUAL_MACHINE,
                                                  name=virtual_machine['role_name'],
                                                  cloud_service_id=cs.id)
                    db_adapter.commit()
                    user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, END)
            else:
                user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, START)
                try:
                    result = self.sms.delete_role(cloud_service['service_name'],
                                                  deployment['deployment_name'],
                                                  virtual_machine['role_name'])
                except Exception as e:
                    user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, FAIL, e.message)
                    log.error(e)
                    return False
                # make sure async operation succeeds
                if not wait_for_async(self.sms, result.request_id, ASYNC_TICK, ASYNC_LOOP):
                    m = WAIT_FOR_ASYNC + ' ' + FAIL
                    user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, FAIL, m)
                    log.error(m)
                    return False
                # make sure virtual machine not exist
                if AzureVirtualMachines(self.sms, self.user_template, self.template_config). \
                        role_exists(cloud_service['service_name'],
                                    deployment['deployment_name'],
                                    virtual_machine['role_name']):
                    m = '%s %s deleted but failed' % (VIRTUAL_MACHINE, virtual_machine['role_name'])
                    user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, FAIL, m)
                    log.error(m)
                    return False
                else:
                    # delete vm, cascade delete vm endpoint and vm config
                    db_adapter.delete_all_objects(UserResource,
                                                  user_template_id=user_template.id,
                                                  type=VIRTUAL_MACHINE,
                                                  name=virtual_machine['role_name'],
                                                  cloud_service_id=cs.id)
                    db_adapter.commit()
                    user_operation_commit(self.user_template, DELETE_VIRTUAL_MACHINE, END)
        user_operation_commit(self.user_template, DELETE, END)
        return True

    # --------------------------------------------helper function-------------------------------------------- #

    def __resource_check(self, cloud_service, deployment, virtual_machines, operation):
        """
        Check whether specific cloud service, deployment and virtual machine are in azure and database
        This function is used for update, delete and shutdown operation
        :return:
        """
        # make sure cloud service exist in azure
        if not AzureCloudService(self.sms, self.user_template, self.template_config) \
                .cloud_service_exists(cloud_service['service_name']):
            m = '%s %s not exist in azure' % (CLOUD_SERVICE, cloud_service['service_name'])
            user_operation_commit(self.user_template, operation, FAIL, m)
            log.error(m)
            return None
        # make sure cloud service exist in database
        if db_adapter.count(UserResource, type=CLOUD_SERVICE, name=cloud_service['service_name']) == 0:
            m = '%s %s not exist in database' % (CLOUD_SERVICE, cloud_service['service_name'])
            log.debug(m)
            user_resource_commit(self.user_template, CLOUD_SERVICE, cloud_service['service_name'], RUNNING)
        cs = db_adapter.find_first_object(UserResource, type=CLOUD_SERVICE, name=cloud_service['service_name'])
        # make sure deployment exist in azure
        if not AzureVirtualMachines(self.sms, self.user_template, self.template_config). \
                deployment_exists(cloud_service['service_name'], deployment['deployment_slot']):
            m = '%s %s not exist in azure' % (DEPLOYMENT, deployment['deployment_name'])
            user_operation_commit(self.user_template, operation, FAIL, m)
            log.error(m)
            return None
        # make sure deployment exist in database
        if db_adapter.count(UserResource,
                            type=DEPLOYMENT,
                            name=deployment['deployment_name'],
                            cloud_service_id=cs.id) == 0:
            m = '%s %s not exist in database' % (DEPLOYMENT, deployment['deployment_name'])
            log.debug(m)
            user_resource_commit(self.user_template, DEPLOYMENT, deployment['deployment_name'], RUNNING)
        for virtual_machine in virtual_machines:
            # make sure virtual machine exist in azure
            if not AzureVirtualMachines(self.sms, self.user_template, self.template_config). \
                    role_exists(cloud_service['service_name'],
                                deployment['deployment_name'],
                                virtual_machine['role_name']):
                m = '%s %s not exist in azure' % (VIRTUAL_MACHINE, virtual_machine['role_name'])
                user_operation_commit(self.user_template, operation, FAIL, m)
                log.error(m)
                return None
            # make sure virtual machine of user template exist in database
            if db_adapter.count(UserResource,
                                user_template_id=self.user_template.id,
                                type=VIRTUAL_MACHINE,
                                name=virtual_machine['role_name'],
                                cloud_service_id=cs.id) == 0:
                m = '%s %s not exist in database' % (VIRTUAL_MACHINE, virtual_machine['role_name'])
                user_operation_commit(self.user_template, operation, FAIL, m)
                log.error(m)
                return None
            # make sure virtual machine is not already stopped
            if operation == SHUTDOWN:
                deploy = self.sms.get_deployment_by_name(cloud_service['service_name'], deployment['deployment_name'])
                for role_instance in deploy.role_instance_list:
                    if role_instance.instance_name == virtual_machine['role_name']:
                        if role_instance.instance_status == STOPPED_VM \
                                or role_instance.instance_status == STOPPED_DEALLOCATED:
                            m = '%s is already stopped' % VIRTUAL_MACHINE
                            user_operation_commit(self.user_template, operation, FAIL, m)
                            log.error(m)
                            return None
                        break
                user_resource_status_update(self.user_template,
                                            VIRTUAL_MACHINE,
                                            virtual_machine['role_name'],
                                            RUNNING,
                                            cs.id)
        return cs
