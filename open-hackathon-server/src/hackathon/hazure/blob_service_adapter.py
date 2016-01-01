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

from azure.storage.blob import BlobService

from service_adapter import ServiceAdapter

__all__ = ["BlobServiceAdapter"]


class BlobServiceAdapter(ServiceAdapter):
    """The :class:`BlobServiceAdapter` class is a thin wrapper over azure.storage.BlobService.

    All the attributes of the wrapper stream are proxied by the adapter so
    it's possible to do ``adapter.create_container()`` instead of the long form
    ``adapter.blob_service.adapter()``.
    """

    def __init__(self):
        super(BlobServiceAdapter, self).__init__(
            BlobService(account_name=self.util.get_config("storage.azure.account_name"),
                        account_key=self.util.get_config("storage.azure.account_key"),
                        host_base=self.util.get_config("storage.azure.blob_service_host_base")))

    def create_container_in_storage(self, container_name, access="container"):
        """create a container if doesn't exist

        :type container_name: str|unicode
        :param container_name: Name of container to create.

        :type access: str|unicode
        :param access: Optional. Possible values include: container, blob
        :return:
        """
        try:
            names = [x.name for x in self.service.list_containers()]
            if container_name not in names:
                return self.service.create_container(container_name, x_ms_blob_public_access=access)
            else:
                self.log.debug("container already exists in storage")
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
                self.service.put_block_blob_from_file(container_name, blob_name, stream)
                return self.service.make_blob_url(container_name, blob_name)
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
                self.service.put_block_blob_from_bytes(container_name, blob_name, blob)
                return self.service.make_blob_url(container_name, blob_name)
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
                self.service.put_block_blob_from_text(container_name, blob_name, text)
                return self.service.make_blob_url(container_name, blob_name)
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
                self.service.put_block_blob_from_path(container_name, blob_name, path)
                return self.service.make_blob_url(container_name, blob_name)
            else:
                return None
        except Exception as e:
            self.log.error(e)
            return None

    def delete_file_from_azure(self, container_name, blob_name):
        try:
            if self.create_container_in_storage(container_name, 'container'):
                self.service.delete_blob(container_name, blob_name)
        except Exception as e:
            self.log.error(e)
            return None
