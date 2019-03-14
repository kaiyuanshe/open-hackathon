# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

__author__ = "rapidhere"
__all__ = ["QueueServiceAdapter"]

try:
    from azure.storage.queueservice import QueueService
except ImportError:
    from azure.storage.queue import QueueService

from service_adapter import ServiceAdapter


class QueueServiceAdapter(ServiceAdapter):
    """This adapater is a part of AzureStorage Python SDK adapter

    this is just a thin proxy on azure.storage.queueservice.QueueService, and have the same usage as BlobServiceAdapter
    """

    def __init__(self, account_name, account_key, *args, **kwargs):
        super(QueueServiceAdapter, self).__init__(
            QueueService(account_name, account_key, *args, **kwargs))
