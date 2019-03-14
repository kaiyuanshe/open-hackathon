# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

__author__ = "rapidhere"
__all__ = ["TableServiceAdapter"]

try:
    from azure.storage.tableservice import TableService
except ImportError:
    from azure.storage.table import TableService

from service_adapter import ServiceAdapter


class TableServiceAdapter(ServiceAdapter):
    """This adapater is a part of AzureStorage Python SDK adapter

    this is just a thin proxy on azure.storage.tableservice.TableService, and have the same usage as BlobServiceAdapter
    """

    def __init__(self, account_name, account_key, *args, **kwargs):
        super(TableServiceAdapter, self).__init__(
            TableService(account_name, account_key, *args, **kwargs))
