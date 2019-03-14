# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

__author__ = "rapidhere"
__all__ = ["FileServiceAdapter"]

from azure.storage.file import FileService

from service_adapter import ServiceAdapter


class FileServiceAdapter(ServiceAdapter):
    """This adapater is a part of AzureStorage Python SDK adapter

    this is just a thin proxy on azure.storage.file.FileService, and have the same usage as BlobServiceAdapter
    """

    def __init__(self, account_name, account_key, *args, **kwargs):
        super(FileServiceAdapter, self).__init__(
            FileService(account_name, account_key, *args, **kwargs))
