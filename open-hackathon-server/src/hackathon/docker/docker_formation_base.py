# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import abc


class DockerFormationBase(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def start(self, unit, **kwargs):
        """start a docker container"""
        return

    @abc.abstractmethod
    def stop(self, name, **kwargs):
        """stop a docker container"""
        return

    @abc.abstractmethod
    def delete(self, name, **kwargs):
        """delete a docker container"""
        return

    @abc.abstractmethod
    def report_health(self):
        """report health status"""
        return