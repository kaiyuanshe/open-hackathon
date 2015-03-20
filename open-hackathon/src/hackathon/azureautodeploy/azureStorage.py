__author__ = 'Yifu Huang'
import sys
sys.path.append("..")
from azureUtil import *
from hackathon.database.models import *
from hackathon.log import *


class AzureStorage:
    """
    Azure storage is used for azure virtual machines to store their disks
    Note that the number of azure storage account of user may have a small limit
    Currently the status of storage in database is only RUNNING
    """

    def __init__(self, sms, template, template_config):
        self.sms = sms
        self.template = template
        self.template_config = template_config

    def create_storage_account(self):
        """
        If storage account not exist, then create it
        Else check whether it created by this function before
        :return:
        """
        user_operation_commit(self.template, CREATE_STORAGE_ACCOUNT, START)
        storage_account = self.template_config['storage_account']
        # avoid duplicate storage account
        if not self.__storage_account_exists(storage_account['service_name']):
            # delete old info in database
            db_adapter.delete_all_objects_by(UserResource, type=STORAGE_ACCOUNT, name=storage_account['service_name'])
            db_adapter.commit()
            try:
                result = self.sms.create_storage_account(storage_account['service_name'],
                                                         storage_account['description'],
                                                         storage_account['label'],
                                                         location=storage_account['location'])
            except Exception as e:
                user_operation_commit(self.template, CREATE_STORAGE_ACCOUNT, FAIL, e.message)
                log.error(e)
                return False
            # make sure async operation succeeds
            if not wait_for_async(self.sms, result.request_id, ASYNC_TICK, ASYNC_LOOP):
                m = WAIT_FOR_ASYNC + ' ' + FAIL
                user_operation_commit(self.template, CREATE_STORAGE_ACCOUNT, FAIL, m)
                log.error(m)
                return False
            # make sure storage account exists
            if not self.__storage_account_exists(storage_account['service_name']):
                m = '%s %s created but not exist' % (STORAGE_ACCOUNT, storage_account['service_name'])
                user_operation_commit(self.template, CREATE_STORAGE_ACCOUNT, FAIL, m)
                log.error(m)
                return False
            else:
                user_resource_commit(self.template, STORAGE_ACCOUNT, storage_account['service_name'], RUNNING)
                user_operation_commit(self.template, CREATE_STORAGE_ACCOUNT, END)
        else:
            # check whether storage account created by this function before
            if db_adapter.count_by(UserResource, type=STORAGE_ACCOUNT, name=storage_account['service_name']) == 0:
                m = '%s %s exist but not created by this function before' %\
                    (STORAGE_ACCOUNT, storage_account['service_name'])
                user_resource_commit(self.template, STORAGE_ACCOUNT, storage_account['service_name'], RUNNING)
            else:
                m = '%s %s exist and created by this function before' %\
                    (STORAGE_ACCOUNT, storage_account['service_name'])
            user_operation_commit(self.template, CREATE_STORAGE_ACCOUNT, END, m)
            log.debug(m)
        return True

    # --------------------------------------------helper function-------------------------------------------- #

    def __storage_account_exists(self, name):
        """
        Check whether specific storage account exist
        :param name:
        :return:
        """
        try:
            props = self.sms.get_storage_account_properties(name)
        except Exception as e:
            if e.message != 'Not found (Not Found)':
                log.error('%s %s: %s' % (STORAGE_ACCOUNT, name, e))
            return False
        return props is not None