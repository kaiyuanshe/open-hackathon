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

import abc

from hackathon import Component

__all__ = ["Storage"]


class Storage(Component):
    """Base for template storage"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save(self, context):
        """Save a file to storage

        Will load frile from context.content, and save to some place accoring to file_type and file_name.
        After save, return an updated context which includes the url and the physical_path(if any) to caller. You MUST
        keep url in some place and you MAY save physical_path as well for simplicity in some cases.

        the url will be used in 'delete' method as a unique identifier so make sure url is unique in your implementation

        :type context: Context
        :param context: the execution context of file saving. Must contain following keys: file_name, file_type, content

        :rtype context
        :return the updated context which should including the full path of saved file. Must contain url and physical_path
        """
        return

    @abc.abstractmethod
    def delete(self, url):
        """Delete file from storage according to url

        :type url: str|unicode
        :param url: the url of file to be deleted which are created in 'save'

        :rtype bool
        :return True if successfully deleted else False
        """
        return

    @abc.abstractmethod
    def report_health(self):
        """report health status of the storage"""
        return
