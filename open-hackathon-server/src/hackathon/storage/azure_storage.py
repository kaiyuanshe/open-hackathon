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
from storage import Storage
import json

from hackathon import RequiredFeature
from hackathon.constants import FILE_TYPE, HEALTH_STATUS, HEALTH


__all__ = ["AzureStorage"]


class AzureStorage(Storage):
    """Hackathon file storage that saves all templates on Azure storage

    template files will be save at "<hostname>/<container_name>/<blob_name>"
    uploaded images will be save at "<hostname>/<container_name>/<blob_name>"

    """
    cache_manager = RequiredFeature("cache_manager")
    file_service = RequiredFeature("file_service")

    def save(self, context):
        """Save a file to Azure storage

        :type context: Context
        :param context: the execution context of file saving

        :rtype context
        :return the updated context which should including the full path of saved file
        """
        assert ("container_name" in context.keys()) and ("blob_name" in context.keys())
        if "path" in context.keys():
            result = self.file_service.upload_file_to_azure_from_path(context.path,
                                                                      context.container_name,
                                                                      context.blob_name)
            if result is not None:
                self.cache_manager.invalidate(result)
        else:
            assert ("file" in context.keys())
            result = self.file_service.upload_file_to_azure(context.file, context.container_name, context.blob_name)
            if result is not None:
                self.cache_manager.invalidate(result)
        context["azure_file_url"] = result
        return context

    def load(self, context):
        """Load file from storage

        :type context: Context
        :param context: the execution context of file loading

        :rtype dict
        :return the file content
        """
        assert ("azure_file_url" in context) and ("local_file_path" in context)
        path = self.cache_manager.get_cache(key=context.azure_file_url,
                                            createfunc=self.file_service.download_file_from_azure(
                                                context.azure_file_url,
                                                context.local_file_path)
                                            )
        if path is None:
            return None
        file_type = context.file_type
        if file_type == FILE_TYPE.TEMPLATE:
            with open(path) as template_file:
                return json.load(template_file)
        else:
            return None

    def delete(self, context):
        """Delete file from Azure storage

        :type context: Context
        :param context: the execution context of file deleting

        :rtype bool
        :return True if successfully deleted else False
        """
        try:
            self.file_service.delete_file_from_azure(context.container_name, context.blob_name)
            url = self.file_service.blob_service.make_blob_url(context.container_name, context.blob_name)
            self.cache_manager.invaildate(url)
            return True
        except Exception as e:
            self.log.error(e)
            return None

    def report_health(self):
        """The status of Azure storage should be always True"""
        return {
            HEALTH.STATUS: HEALTH_STATUS.OK
        }
