from __future__ import absolute_import
import sys

sys.path.append("..")
from hackathon.azureautodeploy.azureUtil import *
from azure.servicemanagement import *
import datetime


class AzureVirtualMachines:
    """
    Azure virtual machines are a collection of deployment and virtual machine on the deployment
    Currently the status of deployment in database is only RUNNING,
    the status of virtual machine are RUNNING and STOPPED
    """

    def __init__(self, sms, user_template, template_config):
        self.sms = sms
        self.user_template = user_template
        self.template_config = template_config

    def create_virtual_machines(self):
        """
        1. If deployment not exist, then create virtual machine with deployment
           Else check whether it created by this function before
        2. If deployment created by this function before and virtual machine not exist,
            then add virtual machine to deployment
           Else check whether virtual machine created by this function before
        :return:
        """
        user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINES, START)
        storage_account = self.template_config['storage_account']
        container = self.template_config['container']
        cloud_service = self.template_config['cloud_service']
        deployment = self.template_config['deployment']
        virtual_machines = self.template_config['virtual_machines']
        cs = db_adapter.find_first_object(UserResource, type=CLOUD_SERVICE, name=cloud_service['service_name'])
        if cs is None:
            m = '%s %s not running in database now' % (CLOUD_SERVICE, cloud_service['service_name'])
            user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINES, FAIL, m)
            log.error(m)
            return False
        for virtual_machine in virtual_machines:
            user_operation_commit(self.user_template, CREATE_DEPLOYMENT, START)
            user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, START)
            system_config = virtual_machine['system_config']
            # check whether virtual machine is Windows or Linux
            if system_config['os_family'] == WINDOWS:
                config = WindowsConfigurationSet(computer_name=system_config['host_name'],
                                                 admin_password=system_config['user_password'],
                                                 admin_username=system_config['user_name'])
                config.domain_join = None
                config.win_rm = None
            else:
                config = LinuxConfigurationSet(system_config['host_name'],
                                               system_config['user_name'],
                                               system_config['user_password'],
                                               False)
            now = datetime.datetime.now()
            blob = '%s-%s-%s-%s-%s-%s-%s.vhd' % (virtual_machine['source_image_name'],
                                                 str(now.year), str(now.month), str(now.day),
                                                 str(now.hour), str(now.minute), str(now.second))
            media_link = 'https://%s.%s/%s/%s' % (storage_account['service_name'],
                                                  storage_account['url_base'],
                                                  container,
                                                  blob)
            os_hd = OSVirtualHardDisk(virtual_machine['source_image_name'], media_link)
            # remote
            remote = virtual_machine['remote']
            remote_provider = remote['provider']
            remote_protocol = remote['protocol']
            remote_input_endpoint_name = remote['input_endpoint_name']
            gc = {
                'displayname': remote_input_endpoint_name,
                'protocol': remote_protocol,
                "username": system_config['user_name'],
                "password": system_config['user_password']
            }
            network_config = virtual_machine['network_config']
            network = ConfigurationSet()
            network.configuration_set_type = network_config['configuration_set_type']
            input_endpoints = network_config['input_endpoints']
            for input_endpoint in input_endpoints:
                port = int(input_endpoint['local_port'])
                # avoid duplicate vm endpoint under same cloud service
                while db_adapter.count(VMEndpoint, cloud_service_id=cs.id, public_port=port) > 0:
                    port = (port + 1) % 65536
                vm_endpoint_commit(input_endpoint['name'],
                                   input_endpoint['protocol'],
                                   port,
                                   input_endpoint['local_port'],
                                   cs)
                network.input_endpoints.input_endpoints.append(
                    ConfigurationSetInputEndpoint(input_endpoint['name'],
                                                  input_endpoint['protocol'],
                                                  port,
                                                  input_endpoint['local_port']))
                if remote_input_endpoint_name == input_endpoint['name']:
                    gc['port'] = port
            # avoid duplicate deployment
            if self.deployment_exists(cloud_service['service_name'], deployment['deployment_name']):
                if db_adapter.count(UserResource,
                                    type=DEPLOYMENT,
                                    name=deployment['deployment_name'],
                                    cloud_service_id=cs.id) == 0:
                    m = '%s %s exist but not created by this function before' % \
                        (DEPLOYMENT, deployment['deployment_name'])
                    user_resource_commit(self.user_template, DEPLOYMENT, deployment['deployment_name'], RUNNING, cs.id)
                else:
                    m = '%s %s exist and created by this function before' % \
                        (DEPLOYMENT, deployment['deployment_name'])
                user_operation_commit(self.user_template, CREATE_DEPLOYMENT, END, m)
                log.debug(m)
                # avoid duplicate role
                if self.role_exists(cloud_service['service_name'],
                                    deployment['deployment_name'],
                                    virtual_machine['role_name']):
                    if db_adapter.count(UserResource,
                                        user_template_id=self.user_template.id,
                                        type=VIRTUAL_MACHINE,
                                        name=virtual_machine['role_name'],
                                        cloud_service_id=cs.id) == 0:
                        m = '%s %s exist but not created by this user template before' % \
                            (VIRTUAL_MACHINE, virtual_machine['role_name'])
                        user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, FAIL, m)
                        vm_endpoint_rollback(cs)
                        log.error(m)
                        return False
                    else:
                        m = '%s %s exist and created by this user template before' % \
                            (VIRTUAL_MACHINE, virtual_machine['role_name'])
                        user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, END, m)
                        vm_endpoint_rollback(cs)
                        log.debug(m)
                else:
                    # delete old virtual machine info in database, cascade delete old vm endpoint and old vm config
                    db_adapter.delete_all_objects(UserResource,
                                                  type=VIRTUAL_MACHINE,
                                                  name=virtual_machine['role_name'],
                                                  cloud_service_id=cs.id)
                    db_adapter.commit()
                    try:
                        result = self.sms.add_role(cloud_service['service_name'],
                                                   deployment['deployment_name'],
                                                   virtual_machine['role_name'],
                                                   config,
                                                   os_hd,
                                                   network_config=network,
                                                   role_size=virtual_machine['role_size'])
                    except Exception as e:
                        user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, FAIL, e.message)
                        vm_endpoint_rollback(cs)
                        log.error(e)
                        return False
                    # make sure async operation succeeds
                    if not wait_for_async(self.sms, result.request_id, ASYNC_TICK, ASYNC_LOOP):
                        m = WAIT_FOR_ASYNC + ' ' + FAIL
                        user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, FAIL, m)
                        vm_endpoint_rollback(cs)
                        log.error(m)
                        return False
                    # make sure role is ready
                    if not self.wait_for_role(cloud_service['service_name'],
                                              deployment['deployment_name'],
                                              virtual_machine['role_name'],
                                              VIRTUAL_MACHINE_TICK,
                                              VIRTUAL_MACHINE_LOOP):
                        m = '%s %s created but not ready' % (VIRTUAL_MACHINE, virtual_machine['role_name'])
                        user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, FAIL, m)
                        vm_endpoint_rollback(cs)
                        log.error(m)
                        return False
                    else:
                        user_resource_commit(self.user_template,
                                             VIRTUAL_MACHINE,
                                             virtual_machine['role_name'],
                                             RUNNING,
                                             cs.id)
                        user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, END)
                        self.__vm_info_helper(cs,
                                              cloud_service['service_name'],
                                              deployment['deployment_name'],
                                              virtual_machine['role_name'],
                                              remote_provider,
                                              gc)
            else:
                # delete old deployment
                db_adapter.delete_all_objects(UserResource,
                                              type=DEPLOYMENT,
                                              name=deployment['deployment_name'],
                                              cloud_service_id=cs.id)
                # delete old virtual machine info in database, cascade delete old vm endpoint and old vm config
                db_adapter.delete_all_objects(UserResource,
                                              type=VIRTUAL_MACHINE,
                                              name=virtual_machine['role_name'],
                                              cloud_service_id=cs.id)
                db_adapter.commit()
                try:
                    result = self.sms.create_virtual_machine_deployment(cloud_service['service_name'],
                                                                        deployment['deployment_name'],
                                                                        deployment['deployment_slot'],
                                                                        virtual_machine['label'],
                                                                        virtual_machine['role_name'],
                                                                        config,
                                                                        os_hd,
                                                                        network_config=network,
                                                                        role_size=virtual_machine['role_size'])
                except Exception as e:
                    user_operation_commit(self.user_template, CREATE_DEPLOYMENT, FAIL, e.message)
                    user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, FAIL, e.message)
                    vm_endpoint_rollback(cs)
                    log.error(e)
                    return False
                # make sure async operation succeeds
                if not wait_for_async(self.sms, result.request_id, ASYNC_TICK, ASYNC_LOOP):
                    m = WAIT_FOR_ASYNC + ' ' + FAIL
                    user_operation_commit(self.user_template, CREATE_DEPLOYMENT, FAIL, m)
                    user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, FAIL, m)
                    vm_endpoint_rollback(cs)
                    log.error(m)
                    return False
                # make sure deployment is ready
                if not self.__wait_for_deployment(cloud_service['service_name'],
                                                  deployment['deployment_name'],
                                                  DEPLOYMENT_TICK,
                                                  DEPLOYMENT_LOOP):
                    m = '%s %s created but not ready' % (DEPLOYMENT, deployment['deployment_name'])
                    user_operation_commit(self.user_template, CREATE_DEPLOYMENT, FAIL, m)
                    vm_endpoint_rollback(cs)
                    log.error(m)
                    return False
                else:
                    user_resource_commit(self.user_template, DEPLOYMENT, deployment['deployment_name'], RUNNING, cs.id)
                    user_operation_commit(self.user_template, CREATE_DEPLOYMENT, END)
                # make sure role is ready
                if not self.wait_for_role(cloud_service['service_name'],
                                          deployment['deployment_name'],
                                          virtual_machine['role_name'],
                                          VIRTUAL_MACHINE_TICK,
                                          VIRTUAL_MACHINE_LOOP):
                    m = '%s %s created but not ready' % (VIRTUAL_MACHINE, virtual_machine['role_name'])
                    user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, FAIL, m)
                    vm_endpoint_rollback(cs)
                    log.error(m)
                    return False
                else:
                    user_resource_commit(self.user_template,
                                         VIRTUAL_MACHINE,
                                         virtual_machine['role_name'],
                                         RUNNING,
                                         cs.id)
                    user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINE, END)
                    self.__vm_info_helper(cs,
                                          cloud_service['service_name'],
                                          deployment['deployment_name'],
                                          virtual_machine['role_name'],
                                          remote_provider,
                                          gc)
        user_operation_commit(self.user_template, CREATE_VIRTUAL_MACHINES, END)
        return True

    def deployment_exists(self, service_name, deployment_name):
        """
        Check whether specific deployment exist
        :param service_name:
        :param deployment_name:
        :return:
        """
        try:
            props = self.sms.get_deployment_by_name(service_name, deployment_name)
        except Exception as e:
            if e.message != 'Not found (Not Found)':
                log.error('%s %s: %s' % (DEPLOYMENT, deployment_name, e))
            return False
        return props is not None

    def role_exists(self, service_name, deployment_name, role_name):
        """
        Check whether specific virtual machine exist
        :param service_name:
        :param deployment_name:
        :param role_name:
        :return:
        """
        try:
            props = self.sms.get_role(service_name, deployment_name, role_name)
        except Exception as e:
            if e.message != 'Not found (Not Found)':
                log.error('%s %s: %s' % (VIRTUAL_MACHINE, role_name, e))
            return False
        return props is not None

    def wait_for_role(self, service_name, deployment_name, role_instance_name,
                      second_per_loop, loop, status=READY_ROLE):
        """
        Wait virtual machine until ready, up to second_per_loop * loop
        :param service_name:
        :param deployment_name:
        :param role_instance_name:
        :param second_per_loop:
        :param loop:
        :param status:
        :return:
        """
        count = 0
        props = self.sms.get_deployment_by_name(service_name, deployment_name)
        while self.__get_role_instance_status(props, role_instance_name) != status:
            log.debug('_wait_for_role [%s] loop count: %d' % (role_instance_name, count))
            count += 1
            if count > loop:
                log.error('Timed out waiting for role instance status.')
                return False
            time.sleep(second_per_loop)
            props = self.sms.get_deployment_by_name(service_name, deployment_name)
        return self.__get_role_instance_status(props, role_instance_name) == status

    # --------------------------------------------helper function-------------------------------------------- #

    def __wait_for_deployment(self, service_name, deployment_name, second_per_loop, loop, status=RUNNING):
        """
        Wait for deployment until running, up to second_per_loop * loop
        :param service_name:
        :param deployment_name:
        :param second_per_loop:
        :param loop:
        :param status:
        :return:
        """
        count = 0
        props = self.sms.get_deployment_by_name(service_name, deployment_name)
        while props.status != status:
            log.debug('_wait_for_deployment [%s] loop count: %d' % (deployment_name, count))
            count += 1
            if count > loop:
                log.error('Timed out waiting for deployment status.')
                return False
            time.sleep(second_per_loop)
            props = self.sms.get_deployment_by_name(service_name, deployment_name)
        return props.status == status

    def __get_role_instance_status(self, deployment, role_instance_name):
        """
        Get virtual machine status
        :param deployment:
        :param role_instance_name:
        :return:
        """
        for role_instance in deployment.role_instance_list:
            if role_instance.instance_name == role_instance_name:
                return role_instance.instance_status
        return None

    def __vm_info_helper(self, cs, cs_name, dm_name, vm_name, remote_provider, gc):
        """
        Help to complete vm info
        :param cs:
        :param cs_name:
        :param dm_name:
        :param vm_name:
        :return:
        """
        # associate vm endpoint with specific vm
        vm = db_adapter.find_first_object(UserResource,
                                          user_template=self.user_template,
                                          type=VIRTUAL_MACHINE,
                                          name=vm_name,
                                          cloud_service_id=cs.id)
        gc['name'] = vm.id
        vm_endpoint_update(cs, vm)
        # commit vm config
        deploy = self.sms.get_deployment_by_name(cs_name, dm_name)
        for role in deploy.role_instance_list:
            # to get private ip
            if role.role_name == vm_name:
                public_ip = None
                # to get public ip
                if role.instance_endpoints is not None:
                    public_ip = role.instance_endpoints.instance_endpoints[0].vip
                    gc['hostname'] = public_ip
                vm_config_commit(vm,
                                 deploy.url,
                                 public_ip,
                                 role.ip_address,
                                 remote_provider,
                                 json.dumps(gc),
                                 self.user_template)
                break