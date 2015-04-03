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

from src.azureformation.azureoperation.resourceBase import(
    ResourceBase,
)
from src.azureformation.azureoperation.utility import (
    AZURE_FORMATION,
    MDL_CLS_FUNC,
    commit_azure_log,
    commit_azure_cloud_service,
    contain_azure_cloud_service,
    delete_azure_cloud_service,
    run_job,
)
from src.azureformation.log import (
    log,
)
from src.azureformation.enum import (
    CLOUD_SERVICE,
    ALOperation,
    ALStatus,
    ACSStatus,
)


class CloudService(ResourceBase):
    """
    Cloud service is used as DNS for azure virtual machines
    """
    CREATE_CLOUD_SERVICE_ERROR = [
        '%s [%s] %s',
        '%s [%s] name not available',
        '%s [%s] subscription not enough',
        '%s [%s] created but not exist',
    ]
    CREATE_CLOUD_SERVICE_INFO = [
        '%s [%s] created',
        '%s [%s] exist and created by %s before',
        '%s [%s] exist but not created by %s before',
    ]
    NEED_COUNT = 1

    def __init__(self, azure_key_id):
        super(CloudService, self).__init__(azure_key_id)

    def create_cloud_service(self, experiment_id, template_unit):
        """
        If cloud service not exist in azure subscription, then create it
        Else reuse cloud service in azure subscription
        :return:
        """
        name = template_unit.get_cloud_service_name()
        label = template_unit.get_cloud_service_label()
        location = template_unit.get_cloud_service_location()
        commit_azure_log(experiment_id, ALOperation.CREATE_CLOUD_SERVICE, ALStatus.START)
        # avoid duplicate cloud service in azure subscription
        if not self.service.cloud_service_exists(name):
            # avoid name already taken by other azure subscription
            if not self.service.check_hosted_service_name_availability(name).result:
                m = self.CREATE_CLOUD_SERVICE_ERROR[1] % (CLOUD_SERVICE, name)
                commit_azure_log(experiment_id, ALOperation.CREATE_CLOUD_SERVICE, ALStatus.FAIL, m, 1)
                log.error(m)
                return False
            # avoid no available subscription remained
            if self.subscription.get_available_cloud_service_count() < self.NEED_COUNT:
                m = self.CREATE_CLOUD_SERVICE_ERROR[2] % (CLOUD_SERVICE, name)
                commit_azure_log(experiment_id, ALOperation.CREATE_CLOUD_SERVICE, ALStatus.FAIL, m, 2)
                log.error(m)
                return False
            # delete old azure cloud service in database, cascade delete old azure deployment,
            # old azure virtual machine and old azure end point
            delete_azure_cloud_service(name)
            try:
                self.service.create_hosted_service(name=name,
                                                   label=label,
                                                   location=location)
            except Exception as e:
                m = self.CREATE_CLOUD_SERVICE_ERROR[0] % (CLOUD_SERVICE, name, e.message)
                commit_azure_log(experiment_id, ALOperation.CREATE_CLOUD_SERVICE, ALStatus.FAIL, m, 0)
                log.error(e)
                return False
            # make sure cloud service is created
            if not self.service.cloud_service_exists(name):
                m = self.CREATE_CLOUD_SERVICE_ERROR[3] % (CLOUD_SERVICE, name)
                commit_azure_log(experiment_id, ALOperation.CREATE_CLOUD_SERVICE, ALStatus.FAIL, m, 3)
                log.error(m)
                return False
            else:
                m = self.CREATE_CLOUD_SERVICE_INFO[0] % (CLOUD_SERVICE, name)
                commit_azure_cloud_service(name, label, location, ACSStatus.CREATED, experiment_id)
                commit_azure_log(experiment_id, ALOperation.CREATE_CLOUD_SERVICE, ALStatus.END, m, 0)
                log.debug(m)
        else:
            # check whether cloud service created by azure formation before
            if contain_azure_cloud_service(name):
                m = self.CREATE_CLOUD_SERVICE_INFO[1] % (CLOUD_SERVICE, name, AZURE_FORMATION)
                commit_azure_log(experiment_id, ALOperation.CREATE_CLOUD_SERVICE, ALStatus.END, m, 1)
            else:
                m = self.CREATE_CLOUD_SERVICE_INFO[2] % (CLOUD_SERVICE, name, AZURE_FORMATION)
                commit_azure_cloud_service(name, label, location, ACSStatus.CREATED, experiment_id)
                commit_azure_log(experiment_id, ALOperation.CREATE_CLOUD_SERVICE, ALStatus.END, m, 2)
            log.debug(m)
        # create virtual machine
        run_job(MDL_CLS_FUNC[5], (self.azure_key_id, ), (experiment_id, template_unit))
        return True

    # todo update cloud service
    def update_cloud_service(self):
        raise NotImplementedError

    # todo delete cloud service
    def delete_cloud_service(self):
        raise NotImplementedError