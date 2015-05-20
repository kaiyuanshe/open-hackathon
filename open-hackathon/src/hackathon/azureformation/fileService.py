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

__author__ = 'Bian Hu'

import sys

sys.path.append("..")
from azure.storage import BlobService
from hackathon.hackathon_response import *
from hackathon.functions import get_config, safe_get_config


def generate_blob_service():
    blob_service = BlobService(account_name=get_config("storage.account_name"),
                               account_key=get_config("storage.account_key"),
                               host_base=get_config("storage.blob_service_host_base"))
    return blob_service


def create_container_in_storage(blob_service, container_name, access):
    """
    create a container if doesn't exist
    :param container_name:
    :param access:
    :return:
    """
    try:
        names = map(lambda x: x.name, blob_service.list_containers())
        if container_name not in names:
            blob_service.create_container(container_name, x_ms_blob_public_access=access)
        else:
            log.debug("container already exsit in storage")
    except Exception as e:
        log.error(e)


def upload_file_to_azure(blob_service, file, container_name, blob_name):
    try:
        blob_service.put_block_blob_from_file(container_name, blob_name, file)
        return blob_service.make_blob_url(container_name, blob_name)
    except Exception as e:
        log.error(e)
        return None


def upload_file_to_azure_from_path(blob_service, path, container_name, blob_name):
    try:
        blob_service.put_block_blob_from_path(container_name, blob_name, path)
        return blob_service.make_blob_url(container_name, blob_name)
    except Exception as e:
        log.error(e)
        return None