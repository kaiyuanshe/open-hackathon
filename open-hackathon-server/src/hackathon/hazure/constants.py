# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.

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
