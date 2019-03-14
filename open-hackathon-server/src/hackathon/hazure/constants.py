# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

__author__ = "rapidhere"
__all__ = ["ASYNC_OP_RESULT", "ASYNC_OP_QUERY_INTERVAL", "ASYNC_OP_QUERY_INTERVAL_LONG", "REMOTE_CREATED_RECORD"]


class ASYNC_OP_RESULT:
    SUCCEEDED = "Succeeded"
    IN_PROGRESS = "InProgress"

ASYNC_OP_QUERY_INTERVAL = 10  # in seconds
ASYNC_OP_QUERY_INTERVAL_LONG = 30  # for heavy works like wait of vm ready


class REMOTE_CREATED_RECORD:
    TYPE_CLOUD_SERVICE = "cloud_service"
    TYPE_STORAGE_ACCOUNT = "storage_account"
    TYPE_ADD_VIRTUAL_MACHINE = "add_virtual_machine"
    TYPE_CREATE_VIRTUAL_MACHINE_DEPLOYMENT = "create_virtual_machine_deployment"
