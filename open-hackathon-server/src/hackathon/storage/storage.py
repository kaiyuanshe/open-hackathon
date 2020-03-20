# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")

import abc

from hackathon import Component

__all__ = ["Storage"]


class Storage(Component, metaclass=abc.ABCMeta):
    """Base for template storage"""

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
