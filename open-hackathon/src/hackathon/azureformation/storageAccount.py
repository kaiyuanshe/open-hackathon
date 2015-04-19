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
from hackathon.azureformation.resourceBase import(
    ResourceBase,
)
from hackathon.azureformation.utility import (
    AZURE_FORMATION,
    MDL_CLS_FUNC,
    commit_azure_log,
    commit_azure_storage_account,
    contain_azure_storage_account,
    delete_azure_storage_account,
    run_job,
)
from hackathon.log import (
    log,
)
from hackathon.enum import (
    STORAGE_ACCOUNT,
    ALOperation,
    ALStatus,
    ASAStatus,
)


class StorageAccount(ResourceBase):
    """
    Storage account is used by azure virtual machines to store their disks
    """
    CREATE_STORAGE_ACCOUNT_ERROR = [
        '%s [%s] %s',
        '%s [%s] name not available',
        '%s [%s] subscription not enough',
        '%s [%s] wait for async fail',
        '%s [%s] created but not exist'
    ]
    CREATE_STORAGE_ACCOUNT_INFO = [
        '%s [%s] created',
        '%s [%s] exist and created by %s before',
        '%s [%s] exist but not created by %s before',
    ]
    NEED_COUNT = 1

    def __init__(self, azure_key_id):
        super(StorageAccount, self).__init__(azure_key_id)

    def create_storage_account(self, experiment_id, template_unit):
        """
        If storage account not exist in azure subscription, then create it
        Else reuse storage account in azure subscription
        :return:
        """
        name = template_unit.get_storage_account_name()
        description = template_unit.get_storage_account_description()
        label = template_unit.get_storage_account_label()
        location = template_unit.get_storage_account_location()
        commit_azure_log(experiment_id, ALOperation.CREATE_STORAGE_ACCOUNT, ALStatus.START)
        # avoid duplicate storage account in azure subscription
        if not self.service.storage_account_exists(name):
            # avoid name already taken by other azure subscription
            if not self.service.check_storage_account_name_availability(name).result:
                m = self.CREATE_STORAGE_ACCOUNT_ERROR[1] % (STORAGE_ACCOUNT, name)
                commit_azure_log(experiment_id, ALOperation.CREATE_STORAGE_ACCOUNT, ALStatus.FAIL, m, 1)
                log.error(m)
                return False
            # avoid no available subscription remained
            if self.subscription.get_available_storage_account_count() < self.NEED_COUNT:
                m = self.CREATE_STORAGE_ACCOUNT_ERROR[2] % (STORAGE_ACCOUNT, name)
                commit_azure_log(experiment_id, ALOperation.CREATE_STORAGE_ACCOUNT, ALStatus.FAIL, m, 2)
                log.error(m)
                return False
            # delete old azure storage account in database
            delete_azure_storage_account(name)
            try:
                result = self.service.create_storage_account(name,
                                                             description,
                                                             label,
                                                             location)
            except Exception as e:
                m = self.CREATE_STORAGE_ACCOUNT_ERROR[0] % (STORAGE_ACCOUNT, name, e.message)
                commit_azure_log(experiment_id, ALOperation.CREATE_STORAGE_ACCOUNT, ALStatus.FAIL, m, 0)
                log.error(e)
                return False
            # query async operation status
            run_job(MDL_CLS_FUNC[2],
                    (self.azure_key_id, ),
                    (result.request_id,
                     MDL_CLS_FUNC[3], (self.azure_key_id, ), (experiment_id, template_unit),
                     MDL_CLS_FUNC[4], (self.azure_key_id, ), (experiment_id, template_unit)))
        else:
            # check whether storage account created by azure formation before
            if contain_azure_storage_account(name):
                m = self.CREATE_STORAGE_ACCOUNT_INFO[1] % (STORAGE_ACCOUNT, name, AZURE_FORMATION)
                commit_azure_log(experiment_id, ALOperation.CREATE_STORAGE_ACCOUNT, ALStatus.END, m, 1)
            else:
                m = self.CREATE_STORAGE_ACCOUNT_INFO[2] % (STORAGE_ACCOUNT, name, AZURE_FORMATION)
                commit_azure_storage_account(name, description, label, location, ASAStatus.ONLINE, experiment_id)
                commit_azure_log(experiment_id, ALOperation.CREATE_STORAGE_ACCOUNT, ALStatus.END, m, 2)
            log.debug(m)
            # create cloud service
            run_job(MDL_CLS_FUNC[1], (self.azure_key_id,), (experiment_id, template_unit))
        return True

    def create_storage_account_async_true(self, experiment_id, template_unit):
        name = template_unit.get_storage_account_name()
        description = template_unit.get_storage_account_description()
        label = template_unit.get_storage_account_label()
        location = template_unit.get_storage_account_location()
        # make sure storage account exist
        if not self.service.storage_account_exists(name):
            m = self.CREATE_STORAGE_ACCOUNT_ERROR[4] % (STORAGE_ACCOUNT, name)
            commit_azure_log(experiment_id, ALOperation.CREATE_STORAGE_ACCOUNT, ALStatus.FAIL, m, 4)
            log.error(m)
        else:
            m = self.CREATE_STORAGE_ACCOUNT_INFO[0] % (STORAGE_ACCOUNT, name)
            commit_azure_storage_account(name, description, label, location, ASAStatus.ONLINE, experiment_id)
            commit_azure_log(experiment_id, ALOperation.CREATE_STORAGE_ACCOUNT, ALStatus.END, m, 0)
            log.debug(m)
            # create cloud service
            run_job(MDL_CLS_FUNC[1], (self.azure_key_id,), (experiment_id, template_unit))

    def create_storage_account_async_false(self, experiment_id, template_unit):
        name = template_unit.get_storage_account_name()
        m = self.CREATE_STORAGE_ACCOUNT_ERROR[3] % (STORAGE_ACCOUNT, name)
        commit_azure_log(experiment_id, ALOperation.CREATE_STORAGE_ACCOUNT, ALStatus.FAIL, m, 3)
        log.error(m)

    # todo update storage account
    def update_storage_account(self):
        raise NotImplementedError

    # todo delete storage account
    def delete_storage_account(self):
        raise NotImplementedError