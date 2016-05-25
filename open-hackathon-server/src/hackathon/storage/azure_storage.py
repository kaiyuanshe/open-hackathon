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

import json
import os
from time import strftime
from uuid import uuid1

from werkzeug.datastructures import FileStorage

from hackathon import RequiredFeature
from hackathon.constants import FILE_TYPE, HEALTH_STATUS, HEALTH
from storage import Storage

__all__ = ["AzureStorage"]


class AzureStorage(Storage):
    """Hackathon file storage that saves all templates on Azure storage

    template files will be save at "http://hackathon.blob.core.chinacloudapi.cn/templates/<blob_name>"
    uploaded images will be save at "http://hackathon.blob.core.chinacloudapi.cn/images/<blob_name>"
    """

    def save(self, context):
        """Save a file to Azure storage

        :type context: Context
        :param context: must have {"content":"***", "file_type":"***"} keys

        :rtype: Context
        :return: the updated context which should including the full path of saved file

        :note: in config file, there must exit "storage.azure.image_container",
                            "storage.azure.template_container"
                            and "storage.azure.blob_service_host_base" configuration
        """
        container_name = self.__get_container_by_file_type(context.file_type)
        hackathon_name = context.get("hackathon_name")
        blob_name = self.__generate_file_name(hackathon_name, context.file_type, context.file_name)

        if context.get('content'):
            file_content = context.content
            if isinstance(file_content, file) or isinstance(file_content, FileStorage):
                result = self.azure_blob_service.upload_file_to_azure(container_name, blob_name, file_content)
            elif isinstance(file_content, dict):
                text = json.dumps(file_content)
                result = self.azure_blob_service.upload_file_to_azure_from_text(container_name, blob_name, text)
            else:
                text = str(file_content)
                result = self.azure_blob_service.upload_file_to_azure_from_text(container_name, blob_name, text)
        else:
            assert context.get('file_path')
            file_path = context.file_path
            result = self.azure_blob_service.upload_file_to_azure_from_path(container_name, blob_name, file_path)

        context["url"] = result
        self.log.debug("File saved at:" + result)
        return context

    def delete(self, url):
        """Delete file from Azure storage

        :type url: str|unicode
        :param url: the url of file to be deleted which are created in 'save'

        :rtype: bool
        :return: True if successfully deleted, otherwise False
        """
        try:
            url_arr = url.split('/')
            blob_name = url_arr[-1]
            container_name = url_arr[-2]
            print container_name, blob_name

            self.azure_blob_service.delete_file_from_azure(container_name, blob_name)
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def report_health(self):
        """Report the status of Azure storage"""
        try:
            if self.azure_blob_service.create_container_in_storage('images', 'container'):
                return {
                    HEALTH.STATUS: HEALTH_STATUS.OK,
                    HEALTH.DESCRIPTION: "You can use Azure resources now.",
                    "type": "AzureStorage"
                }
            else:
                return {
                    HEALTH.STATUS: HEALTH_STATUS.ERROR
                }
        except Exception as e:
            self.log.error(e)
            return {
                HEALTH.STATUS: HEALTH_STATUS.ERROR
            }

    def __init__(self):
        self.__containers = {
            FILE_TYPE.TEMPLATE: self.util.safe_get_config("storage.azure.template_container", "templates"),
            FILE_TYPE.HACK_IMAGE: self.util.safe_get_config("storage.azure.image_container", "images"),
            FILE_TYPE.AZURE_CERT: self.util.safe_get_config("storage.azure.certificate_container", "certificate"),
            FILE_TYPE.USER_FILE: self.util.safe_get_config("storage.azure.user_file_container", "userfile"),
            FILE_TYPE.TEAM_FILE: self.util.safe_get_config("storage.azure.team_file_container", "teamfile"),
            FILE_TYPE.HACK_FILE: self.util.safe_get_config("storage.azure.hack_file_container", "hackfile"),
        }
        self.azure_blob_service = RequiredFeature("azure_blob_service")

    def __get_container_by_file_type(self, file_type):
        """Get container name of azure by file type

        :type file_type: str| unicode
        :param file_type: type of file defined at FILE_TYPE in constants.py
        """
        if file_type in self.__containers:
            return self.__containers[file_type]
        return "default"

    @staticmethod
    def __generate_file_name(hackathon_name, file_type, file_name):
        """refresh file_name = hack_name + uuid(10) + time + suffix

        Only image name will be replaced since it may contain Chinese characters
        """
        if file_type == FILE_TYPE.HACK_IMAGE:
            suffix = file_name.split('.')[-1]
            hackathon_name = "" if hackathon_name is None else hackathon_name + "/"
            real_name = hackathon_name + str(uuid1())[0:9] + strftime("%Y%m%d%H%M%S") + "." + suffix
            return real_name
        else:
            return strftime("%Y%m%d/") + file_name
