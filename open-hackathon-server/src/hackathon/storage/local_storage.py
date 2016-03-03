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

import os
from os.path import realpath, dirname, isfile, abspath
import json
import time
import uuid
from werkzeug.datastructures import FileStorage

from hackathon.constants import FILE_TYPE, HEALTH_STATUS, HEALTH
from storage import Storage

__all__ = ["LocalStorage"]


class LocalStorage(Storage):
    """Hackathon file storage that saves all templates on local disk

    files will be save at "<src_dir>/open-hackathon-server/src/hackathon/upload/<file_type>"
    """

    def save(self, context):
        """Save a file to storage

        :type context: Context
        :param context: the execution context of file saving

        :rtype context
        :return the updated context which should including the full path of saved file
        """
        context = self.__generate_paths(context)
        self.__save_file(context.content, context.physical_path)
        self.log.debug("file saved at:" + context.physical_path)
        return context

    def delete(self, url):
        """Delete file from storage

        :type url: str|unicode
        :param url: the url of file to be deleted which are created in 'save'

        :rtype bool
        :return True if successfully deleted else False
        """
        path = self.__convert_url_to_physical_path(url)
        if isfile(path):
            os.remove(path)
            return True
        else:
            self.log.warn("try to remove dir or non-existed file")
            return False

    def report_health(self):
        """The status of local storage should be always True"""
        return {
            HEALTH.STATUS: HEALTH_STATUS.OK,
            "type": "LocalStorage"
        }

    def __init__(self):
        self.base_dir = self.__get_storage_base_dir()

    @staticmethod
    def __ensure_dir(file_path):
        """Make sure the directory of target file exists"""
        path = dirname(file_path)
        if path and not (os.path.exists(path)):
            os.makedirs(path)
        return path

    def __save_file(self, content, path):
        """Dump file to disk

        An existing file with the same name will be erased

        :type content: file | dict | FileStorage
        :param content: the content of file to be saved. Can be a file object or a dict

        :type path: str | unicode
        :param path: the file path
        """
        self.__ensure_dir(path)
        with open(path, 'w') as f:
            if isinstance(content, dict):
                json.dump(content, f)
            elif isinstance(content, file) or isinstance(content, FileStorage):
                f.write(content.read())
            else:
                f.write(str(content))

    @staticmethod
    def __get_storage_base_dir():
        """Get the base directory of storage"""
        return abspath("%s/.." % dirname(realpath(__file__)))

    def __generate_paths(self, context):
        """Generate file new name ,physical path and uri

        :type context: Context
        :param context: execution context

        :return updated context
        """
        hackathon_name = context.hackathon_name if "hackathon_name" in context else None
        # replace file_name with new random name
        context.file_name = self.__generate_file_name(context.file_name, context.file_type, hackathon_name)
        context.physical_path = self.__generate_physical_path(context.file_name, context.file_type)
        context.url = self.__convert_physical_path_to_url(context.physical_path)

        return context

    def __convert_url_to_physical_path(self, url):
        """Return the physical_path according to its url

        :type url: str|unicode
        :param url: the absolute physical path of the file

        :rtype str
        :return public accessable URI
        """
        # physical_path example: <base_dir>/static/upload/hack_image/hack01/20150708/win10-20140708-1234.jpg
        # url example: http://localhost:15000/static/upload/hack_image/hack01/20150708/win10-20140708-1234.jpg
        i = url.index("static")
        path = url[i:]
        return "%s/%s" % (self.base_dir, path)

    def __convert_physical_path_to_url(self, physical_path):
        """Return the http URI according to physical_path

        :type physical_path: str|unicode
        :param physical_path: the absolute physical path of the file

        :rtype str
        :return public accessable URI
        """
        # physical_path example: <base_dir>/static/upload/hack_image/hack01/20150708/win10-20140708-1234.jpg
        # url example: http://localhost:15000/static/upload/hack_image/hack01/20150708/win10-20140708-1234.jpg
        i = physical_path.index("static")
        path = physical_path[i:]
        return self.util.get_config("endpoint") + "/" + path

    def __generate_physical_path(self, file_name, file_type, hackathon_name=None):
        """Return the physical path of file including directory and file name

        files are saved at <base_dir>/static/upload/<file_type>/

        :type file_name: str|unicode
        :param file_name: the original file name

        :type file_type: str | unicode
        :param file_type: type of file which decides the directories where file is saved.

        :rtype str
        :return physical path of the file to be saved
        """
        # <base_dir>/static/upload/<file_type>/<hackathon_name>/<date>/<file_name>
        path = "%s/static/upload/%s%s/%s/%s" % (
            self.base_dir,
            file_type,
            "/" + hackathon_name if hackathon_name else "",
            time.strftime("%Y%m%d"),
            file_name)
        return path

    @staticmethod
    def __generate_file_name(origin_name, file_type, hackathon_name=None):
        """Generate a random file name if file_type is hack_image

        :type origin_name: str | unicode
        :param origin_name the origin name of file

        :type file_type: str|unicode
        :param file_type: type of file, defined by FILTE_TYPE in constants.py

        :type hackathon_name: str | unicode
        :param hackathon_name: name of hackathon related to this file

        :rtype str
        :return a random file name which includes hackathon_name and time as parts
        """
        if not hackathon_name:
            hackathon_name = ""

        # handle uploaded images only since the uploaded file name can be very strange or contains Chinese
        if file_type == FILE_TYPE.HACK_IMAGE:
            extension = os.path.splitext(origin_name)[1]
            new_name = "%s-%s-%s%s" % (
                hackathon_name,
                time.strftime("%Y%m%d"),
                str(uuid.uuid1())[0:8],
                extension
            )
            return new_name.strip('-')
        else:
            return origin_name
