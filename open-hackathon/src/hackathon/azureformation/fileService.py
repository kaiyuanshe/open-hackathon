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
from hackathon import Component


class FileService(Component):
    def __init__(self):
        self.blob_service = None

    def generate_blob_service(self):
        if self.blob_service is None:
            # if storage info doesn't exist in config.py upload file function stop working
            self.blob_service = BlobService(account_name=self.util.get_config("storage.account_name"),
                                            account_key=self.util.get_config("storage.account_key"),
                                            host_base=self.util.get_config("storage.blob_service_host_base"))


    def create_container_in_storage(self, container_name, access):
        """
        create a container if doesn't exist
        :param container_name:
        :param access:
        :return:
        """
        self.generate_blob_service()
        try:
            names = map(lambda x: x.name, self.blob_service.list_containers())
            if container_name not in names:
                self.blob_service.create_container(container_name, x_ms_blob_public_access=access)
            else:
                self.log.debug("container already exsit in storage")
            return True
        except Exception as e:
            self.log.error(e)
            return False


    def upload_file_to_azure(self, file, container_name, blob_name):
        try:
            if self.create_container_in_storage(container_name, 'container'):
                self.blob_service.put_block_blob_from_file(container_name, blob_name, file)
                return self.blob_service.make_blob_url(container_name, blob_name)
            else:
                return None
        except Exception as e:
            self.log.error(e)
            return None


    def upload_file_to_azure_from_path(self, path, container_name, blob_name):
        try:
            if self.create_container_in_storage(container_name, 'container'):
                self.blob_service.put_block_blob_from_path(container_name, blob_name, path)
                return self.blob_service.make_blob_url(container_name, blob_name)
            else:
                return None
        except Exception as e:
            self.log.error(e)
            return None


    def download_file_from_azure(self, container_name, blob_name, local_file):
        try:
            self.blob_service.get_blob_to_file(container_name, blob_name, local_file)
            return local_file
        except Exception as e:
            self.log.error(e)
            return None

