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

import sys

sys.path.append("..")
from azure.storage import BlobService
from hackathon import Component


class FileService(Component):
    def __init__(self):
        self.blob_service = BlobService(account_name=self.util.get_config("storage.azure.account_name"),
                                        account_key=self.util.get_config("storage.azure.account_key"),
                                        host_base=self.util.get_config("storage.azure.blob_service_host_base"))

    def create_container_in_storage(self, container_name, access):
        """
        create a container if doesn't exist
        :param container_name:
        :param access:
        :return:
        """
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

    def upload_file_to_azure(self, container_name, blob_name, stream):
        """
        Creates a new block blob from a file/stream, or updates the content of
        an existing block blob, with automatic chunking and progress
        notifications.

        :type container_name: str|unicode
        :param container_name: Name of existing container.

        :type blob_name: str | unicode
        :param blob_name: Name of blob to create or update.

        :type stream: file
        :param stream: Opened file/stream to upload as the blob content.
        """
        try:
            if self.create_container_in_storage(container_name, 'container'):
                self.blob_service.put_block_blob_from_file(container_name, blob_name, stream)
                return self.blob_service.make_blob_url(container_name, blob_name)
            else:
                return None
        except Exception as e:
            self.log.error(e)
            return None

    def upload_file_to_azure_from_bytes(self, container_name, blob_name, blob):
        """
        Creates a new block blob from an array of bytes, or updates the content
        of an existing block blob, with automatic chunking and progress
        notifications.

        :type container_name: str|unicode
        :param container_name: Name of existing container.

        :type blob_name: str|unicode
        :param blob_name: Name of blob to create or update.

        :type blob: bytes
        :param blob: Content of blob as an array of bytes.
        """
        try:
            if self.create_container_in_storage(container_name, 'container'):
                self.blob_service.put_block_blob_from_bytes(container_name, blob_name, blob)
                return self.blob_service.make_blob_url(container_name, blob_name)
            else:
                return None
        except Exception as e:
            self.log.error(e)
            return None

    def upload_file_to_azure_from_text(self, container_name, blob_name, text):
        """
        Creates a new block blob from str/unicode, or updates the content of an
        existing block blob, with automatic chunking and progress notifications.

        :type container_name: str|unicode
        :param container_name: Name of existing container.

        :type blob_name: str|unicode
        :param blob_name: Name of blob to create or update.

        :type text: str|unicode
        :param text: Text to upload to the blob.
        """
        try:
            if self.create_container_in_storage(container_name, 'container'):
                self.blob_service.put_block_blob_from_text(container_name, blob_name, text)
                return self.blob_service.make_blob_url(container_name, blob_name)
            else:
                return None
        except Exception as e:
            self.log.error(e)
            return None

    def upload_file_to_azure_from_path(self, container_name, blob_name, path):
        """
        Creates a new page blob from a file path, or updates the content of an
        existing page blob, with automatic chunking and progress notifications.

        :type container_name: str|unicode
        :param container_name: Name of existing container.

        :type blob_name: str|unicode
        :param blob_name: Name of blob to create or update.

        :type path: str|unicode
        :param path: Path of the file to upload as the blob content.
        """
        try:
            if self.create_container_in_storage(container_name, 'container'):
                self.blob_service.put_block_blob_from_path(container_name, blob_name, path)
                return self.blob_service.make_blob_url(container_name, blob_name)
            else:
                return None
        except Exception as e:
            self.log.error(e)
            return None

    def delete_file_from_azure(self, container_name, blob_name):
        try:
            if self.create_container_in_storage(container_name, 'container'):
                self.blob_service.delete_blob(container_name, blob_name)
        except Exception as e:
            self.log.error(e)
            return None
