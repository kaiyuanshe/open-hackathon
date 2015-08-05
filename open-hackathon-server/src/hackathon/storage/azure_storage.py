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
__author__ = 'ZGQ'

from storage import Storage
import json
from uuid import uuid1
from time import strftime
from flask import g


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
        :param context: must have {"content":"***", "file_type":"***"} keys

        :rtype context
        :return the updated context which should including the full path of saved file

        :config requirements: in config file, there must exit "storage.azure.image_container",
                            "storage.azure.template_container"
                            and "storage.azure.blob_service_host_base" configuration
        """
        if context.file_type == FILE_TYPE.HACK_IMAGE:
            container_name = self.util.get_config("storage.azure.image_container")
        else:
            container_name = self.util.get_config("storage.azure.template_container")
        blob_name = self.__generate_file_name(context.file_name)

        if context.get('content'):
            file_content = context.content
            result = self.file_service.upload_file_to_azure(file_content, container_name, blob_name)
        else:
            assert context.get('file_path')
            file_path = context.file_path
            result = self.file_service.upload_file_to_azure_from_path(file_path, container_name, blob_name)

        if result is not None:
            self.cache_manager.invalidate(result)
        context["url"] = result
        self.log.debug("File saved at:" + result)
        return context

    def load(self, context):
        """Load file from storage

        :type context: Context
        :param context: the execution context of file loading

        :rtype dict
        :return the file content
        """
        assert context.get("url")
        print context.url, context.path

        def get_temp():
            temp_path = self.file_service.download_file_from_azure(azure_file_url=context.url,
                                                                   local_file_path=context.path)
            if temp_path is None:
                return None
            if context.file_type == FILE_TYPE.TEMPLATE:
                with open(temp_path) as template_file:
                    return json.load(template_file)
            else:
                return None

        return self.cache_manager.get_cache(key=context.url, createfunc=get_temp)

    def delete(self, context):
        """Delete file from Azure storage

        :type context: Context
        :param context: must have {"url":""} key or {"container_name":"***","blob_name":"***"} keys

        :rtype bool
        :return True if successfully deleted else False
        """
        try:
            if context.get("url"):
                url_arr = context.url.split('/')
                file_name = url_arr[-1]
                hackathon_name = url_arr[-2]
                container_name = url_arr[-3]
                blob_name = hackathon_name + "/" + file_name
                print container_name, blob_name
            else:
                assert context.get("container_name") and context.get("blob_name")
                container_name = context.container_name
                blob_name = context.blob_name
            self.file_service.delete_file_from_azure(container_name, blob_name)
            url = self.file_service.blob_service.make_blob_url(container_name, blob_name)
            self.cache_manager.invalidate(url)
            return True
        except Exception as e:
            self.log.error(e)
            return None

    def report_health(self):
        """The status of Azure storage should be always True"""
        return {
            HEALTH.STATUS: HEALTH_STATUS.OK
        }

    def __generate_file_name(self, file_name):
        """refresh file_name = hack_name + uuid(10) + time + suffix
        """
        suffix = file_name.split('.')[-1]
        real_name = g.hackathon.name + "/" + str(uuid1())[0:9] + strftime("%Y%m%d%H%M%S") + "." + suffix
        return real_name
