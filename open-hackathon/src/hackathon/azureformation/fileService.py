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
import imghdr
from azure.storage import BlobService
from flask import g
from hackathon.hackathon_response import *
from hackathon.functions import get_config, safe_get_config

blob_service = BlobService(account_name=get_config("storage.account_name"),
                           account_key=get_config("storage.account_key"),
                           host_base='.blob.core.chinacloudapi.cn')
container_name = safe_get_config("storage.container_name", "filestorage")


def create_container_in_storage():
    # create a container if doesn't exist
    try:
        names = map(lambda x: x.name, blob_service.list_containers())
        if container_name not in names:
            blob_service.create_container(container_name)
        else:
            log.debug("container already exsit in storage")
    except Exception:
        raise


def upload_file_to_azure(file, filename):
    try:
        blob_service.put_block_blob_from_file(container_name, filename, file)
        return blob_service.make_blob_url(container_name, filename)
    except Exception:
        raise


def upload_file(request):
    log.debug("request to upload a file")
    # storage account info must be exist in config file
    if get_config("storage.account_name") is None or get_config("storage.account_key") is None:
        return internal_server_error("can not found storage account info in config file ")

    # check whole request size
    if request.content_length > len(request.files) * get_config("storage.size_limit"):
        return bad_request("more than the file size limited")

    try:
        # check each file type
        for file_name in request.files:
            if imghdr.what(request.files.get(file_name)) is None:
                return bad_request("only images can be uploaded")

        create_container_in_storage()
        images = {}
        for file_name in request.files:
            file = request.files.get(file_name)
            url = upload_file_to_azure(file, g.hackathon.name + "/" + file_name)
            images[file_name] = url

        return images

    except Exception as ex:
        log.error(ex)
        log.error("upload file raised an exception")
        return internal_server_error("upload file raised an exception")

