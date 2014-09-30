#coding=utf-8
from azure import MANAGEMENT_HOST
from azure.servicemanagement import *
import datetime,constants

'''
    This service should fulfill these task:
        1.Create a Virtual Machine both in linux and windows
        2.Delete a Virtual Machine
'''

class AzureService():
    def __init__(self, subscription_id=None, cert_file=None, host=MANAGEMENT_HOST):  # 'management.core.chinacloudapi.cn'
        self.sms = ServiceManagementService(constants.SUBSCRIPTION_ID, constants.CERT_FILE)
        self.__host_instance_count=dict()
        
        #when creating a new virtual machine, set its account with default username and password
        self.__default_username=None
        self.__default_password=None

#------------------------------private helper functions----------------------------------------------------------------
    def __vm_info(self, lab, hostname, endpoints, operating_system):
        '''
        Form a dict using the lab, hostname, endpoints, operating_system, username by default, password by default
        return 
        '''
        vm = dict()
        vm['lab'] = lab
        vm['hostname'] = hostname
        vm['username'] = 'opentech'
        vm['password'] = '@dministrat0r'
        if operating_system == 'linux':
            # local port for SSH is 22
            for point in endpoints:
                if point.local_port == 22:
                    vm['port'] = point.port
                    break
        else:
            # local port for RDP is 3389
            for point in endpoints:
                if point.local_port == 3389:
                    vm['port'] = point.port
                    break
        return vm
        
    def __linux_config(self, hostname):
        linux_config = LinuxConfigurationSet(hostname, 'opentech', '@dministrat0r', True)
        linux_config.disable_ssh_password_authentication = False
        return linux_config
    
    def __generate_blob_name(self, os_type):
        now = datetime.datetime.now()
        target = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second) + os_type + '.vhd'
        return target
    
    def __image_list(self):
        image_list = self.sms.list_os_images()
        return image_list
    
    def __os_hd(self, image_name, target_container_name, os_type='linux'):
        target_blob_name = self.__generate_blob_name(os_type)
        media_link = target_container_name + '/' + target_blob_name
        os_hd = OSVirtualHardDisk(image_name, media_link, disk_label=target_blob_name)
        return os_hd
    
    # need to be dynamic allocated
    def __network_config(self):
        network_config = ConfigurationSet()
        network_config.configuration_set_type = 'NetworkConfiguration'
        network_config.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('ssh', 'tcp', '22', '22'))
        network_config.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('vnc', 'tcp', '5900', '5900'))
        network_config.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('http', 'tcp', '80', '80'))
        network_config.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('http2', 'tcp', '8080', '8080'))
        network_config.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('rdp', 'tcp', '3389', '3389'))
        network_config.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('https', 'tcp', '443', '443'))
        return network_config
#------------------------------private helper functions----------------------------------------------------------------
    

    def create_storage(self, storage_name):
        self.sms.create_storage_account(storage_name, label=storage_name, location=constants.LOCATION)
        
    def check_hosted_service_exist(self, hosted_service_name):
        hosted_services = self.sms.list_hosted_services()
        for service in hosted_services:
            if hosted_service_name == service.service_name:
                return True
        return False
    
    def create_linux_vm(self, hosted_service_name, deployment_name, lab_name=None):
        '''
        Create a linux server, Return the virtual machine
        
        service_name: Name of the hosted service
        deployment_name: Name of the virtual machine, it must be unique among other virtual machines for the hosted service
        lab_name: Name of the lab, such as python, lucene, hadoop...
        
        '''
        hosted_service_exist = self.check_hosted_service_exist(hosted_service_name)
        if hosted_service_exist == False:
            self.sms.create_hosted_service(service_name=hosted_service_name, label=hosted_service_name, description=None,
                                           location=constants.LOCATION, affinity_group=None, extended_properties=None);
        linux_config = self.__linux_config(deployment_name)
        os_hd = self.__os_hd(constants.LINUX_IMAGE, constants.CONTAINER_NAME, 'linux')  # may be windows
        network_config = self.__network_config()
        self.sms.create_virtual_machine_deployment(hosted_service_name, deployment_name, 'production', deployment_name,
                                                   deployment_name, linux_config, os_hd, network_config, role_size='Small')
        self.__host_instance_count[hosted_service_name] = self.__host_instance_count[hosted_service_name]+1         
        info = self.__vm_info(lab_name, hosted_service_name, network_config.input_endpoints)        
        return info
    
    def config_linux_vm(self):
        'scp all the needed scripts, no matter python or bash, to the target virtual machine which was just created'
        pass
    
    def create_windows_vm(self, hosted_service_name, deployment):
        pass
    
    def capture_image(self,hosted_service_name,deployment_name,role_name,image_name,image_label):
        pass
    
if __name__ == '__main__':
    ass = AzureService()
    #ass.create_linux_vm('kangjihua', 'kangjihua')
