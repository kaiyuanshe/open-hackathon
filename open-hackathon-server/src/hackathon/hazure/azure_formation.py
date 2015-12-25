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

__author__ = "rapidhere"


from hackathon import Component, Context

from cloud_service_adapter import CloudServiceAdapter


class AzureFormation(Component):
    """The high level Azure Resource Manager

    the main purpose of this class is to manage the Azure VirtualMachine
    but Azure VirtualMachine depends on lots of Azure Resources like CloudService and Deployment
    this class will manage all of this resouces, like a formation of Azure Resources

    dislike the old AzureFormation class, this class depend on independ Azure Service Adapters to
    finish its job, this is just a high level intergration of these adapters

    usage: RequiredFeature("azuire_formation").setup(template_unit)
    """
    def __init__(self):
        pass

    def setup(self, azure_key, unit):
        """setup the resources needed by the template unit

        this will create the missed VirtualMachine, CloudService and Storages
        this function is not blocked, it will run in the background and return immediatly

        :param unit: a AzureTemplateUnit, contains the data need by azure formation
        :param azure_key: the azure_key object, use to access azure
        """
        ctx = Context(
            azure_template_unit=unit,
            azure_key=azure_key)
        self.scheduler.add_once("azure_formation", "__schedule_setup", context=ctx, seconds=3)

    def stop_vm(self):
        """stop the virtual machine
        """
        pass

    def start_vm(self):
        """start the virtual machine
        """
        pass

    # private functions
    def __schedule_setup(self, ctx):
        self.log.debug("azure formation '%r' setup progress begin" % ctx)
        unit = ctx.azure_template_unit
        azure_key = ctx.azure_key

        self.__setup_cloud_service(azure_key, unit)
        self.log.debug("azure formation '%r': cloud service setup done" % ctx)

        self.__setup_storage(azure_key, unit)
        self.log.debug("azure formation '%r': storage setup done" % ctx)

        self.__setup_virtual_machine(azure_key, unit)
        self.log.debug("azure formation '%r' : virtual machine setup done" % ctx)

    def __setup_cloud_service(self, azure_key, unit):
        name = unit.get_cloud_service_name()
        label = unit.get_cloud_service_label()
        location = unit.get_cloud_service_location()

        adapter = CloudServiceAdapter(
            subscription_id=azure_key.subscription_id,
            pem_url=azure_key.pem_url,
            host=azure_key.management_host)

        if not adapter.create_cloud_service(azure_key.id, name, label, location):
            pass  # TODO: handle failing

    def __setup_storage(self, azure_key, unit):
        pass

    def __setup_virtual_machine(self, azure_key, unit):
        pass
