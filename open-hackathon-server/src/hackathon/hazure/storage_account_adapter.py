# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

__author__ = "rapidhere"
__all__ = ["StorageAccountAdapter"]

from azure.servicemanagement.servicemanagementservice import ServiceManagementService
from azure.common import AzureHttpError, AzureMissingResourceHttpError

from service_adapter import ServiceAdapter
from constants import ASYNC_OP_RESULT


class StorageAccountAdapter(ServiceAdapter):
    """A thin wrapper on ServiceManagementServie class

    wrap up some interface to work with Azure Storage Account
    """
    def __init__(self, subscription_id, cert_url, *args, **kwargs):
        super(StorageAccountAdapter, self).__init__(
            ServiceManagementService(subscription_id, cert_url, *args, **kwargs))

    def storage_account_exists(self, name):
        """Link to azure and check whether specific storage account exist in specific azure subscription

        :type name: string|unicode
        :param name: the name of the storage account

        :rtype: boolean
        :return:
        """
        try:
            props = self.service.get_storage_account_properties(name)
        except AzureMissingResourceHttpError:
            return False
        except Exception as e:
            self.log.error(e)
            raise e

        return props is not None

    def create_storage_account(self, name, description, label, location, **extra):
        """just the sync version of ServiceManagementServie.create_storage_account

        for full list of arguments, please refer to ServiceManagementService.create_storage_account

        NOTE: the creation of storage account may take up a lot of time, and may cause timeout error in this
        sync function, please consider use the async way

        :rtype: boolean
        :return: True on success
        """
        try:
            req = self.service.create_storage_account(
                service_name=name,
                description=description,
                label=label,
                location=location,
                **extra)
        except AzureHttpError as e:
            self.log.debug("create storage account %s failed: %s" % (name, e.message))
            return False

        self.log.debug("storage account %s, creation in progress" % name)
        res = self.service.wait_for_operation_status(
            req.request_id,
            timeout=1800,  # to avoid timeout error
            progress_callback=None,
            success_callback=None,
            failure_callback=None)

        if res and res.status == ASYNC_OP_RESULT.SUCCEEDED:
            if self.storage_account_exists(name):
                self.log.debug("storage account %s, creation done" % name)
                return True

        self.log.debug("storage account %s, creation failed" % name)
        return False

    def update_storage_account(self):
        # TODO
        raise NotImplemented

    def delete_storage_account(self, service_name):
        """delete a storage account from azure

        this is the sync wrapper of ServiceManagementService.delete_storage_account
        """
        try:
            req = self.service.delete_storage_account(service_name)
        except Exception as e:
            self.log.error("delete storage account failed %r" % service_name)
            raise e

        res = self.service.wait_for_operation_status(
            req.request_id,
            timeout=1800,  # to avoid timeout error
            progress_callback=None,
            success_callback=None,
            failure_callback=None)

        if res and res.status == ASYNC_OP_RESULT.SUCCEEDED:
            self.log.debug("storage account %s, delete done" % service_name)
        else:
            self.log.debug("storage account %s, delete failed" % service_name)
