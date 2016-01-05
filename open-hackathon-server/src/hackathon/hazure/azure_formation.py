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
from hackathon.database import AzureCloudService
from hackathon.constants import ACSStatus

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

    def setup(self, azure_key, template):
        """setup the resources needed by the template unit

        this will create the missed VirtualMachine, CloudService and Storages
        this function is not blocked, it will run in the background and return immediatly

        :param template: the azure template, contains the data need by azure formation
        :param azure_key: the azure_key object, use to access azure
        """
        # the setup of each unit must be SERLIALLY EXECUTED
        # to avoid the creation of same resource in same time
        # TODO: we still have't void the parrallel excution of the setup of same template
        job_ctxs = []
        ctx = Context(job_ctxs=job_ctxs, current_job_index=0)

        for unit in template.units:
            job_ctxs.append(Context(
                cloud_service_name=unit.get_cloud_service_name(),
                cloud_service_label=unit.get_cloud_service_label(),
                cloud_service_host=unit.get_cloud_service_location(),

                azure_key_id=azure_key.id,
                subscription_id=azure_key.subscription_id,
                pem_url=azure_key.pem_url,
                management_host=azure_key.management_host))

        # execute from first job context
        self.scheduler.add_once("azure_formation", "schedule_setup", context=ctx, seconds=0)

    def stop_vm(self):
        """stop the virtual machine
        """
        pass

    def start_vm(self):
        """start the virtual machine
        """
        pass

    # private functions
    def schedule_setup(self, ctx):
        current_job_index = ctx.current_job_index
        job_ctxs = ctx.job_ctxs

        if current_job_index >= len(job_ctxs):
            self.log.debug("azure virtual environment setup finish")
            return True

        # excute current setup from setup cloud service
        # whole stage:
        #   setup_cloud_service -> setup_storage -> setup_virtual_machine ->(index + 1) schedule_setup
        # on whatever stage when error occurs, will turn into __on_setup_failed
        self.log.debug(
            "azure virtual environment %d: '%r' setup progress begin" %
            (current_job_index, job_ctxs[current_job_index]))
        self.scheduler.add_once("azure_formation", "setup_cloud_service", context=ctx, seconds=0)

    def __on_setup_failed(self, sctx):
        # TODO: rollback
        pass

        # after rollback done, step into next unit
        sctx.current_job_index += 1
        self.scheduler.add_once("azure_formation", "schedule_setup", context=sctx, seconds=0)

    def setup_cloud_service(self, sctx):
        # get context from super context
        ctx = sctx.job_ctxs[sctx.current_job_index]

        adapter = CloudServiceAdapter(
            ctx.subscription_id,
            ctx.pem_url,
            host=ctx.management_host)

        name = ctx.cloud_service_name
        label = ctx.cloud_service_label
        location = ctx.cloud_service_host
        azure_key_id = ctx.azure_key_id

        try:
            if not adapter.cloud_service_exists(name):
                if not adapter.create_cloud_service(
                        name=name,
                        label=label,
                        location=location):
                    self.log.error("azure virtual environment %d create remote cloud service failed via creation" %
                                   sctx.current_job_index)
                    self.__on_setup_failed(sctx)
                    return

                # first delete the possible old CloudService
                # TODO: is this necessary?
                self.db.delete_all_objects_by(AzureCloudService, name=name)
        except Exception:
            self.log.error("azure virtual environment %d create remote cloud service failed" % sctx.current_job_index)
            self.__on_setup_failed(sctx)
            return

        # update the table
        if self.db.count_by(AzureCloudService, name=name) == 0:
            self.db.add_object_kwargs(
                AzureCloudService,
                name=name,
                label=label,
                location=location,
                status=ACSStatus.CREATED,
                azure_key_id=azure_key_id)

        # commit changes
        self.db.commit()
        self.log.debug("azure virtual environment %d cloud service setup done" % sctx.current_job_index)

        # next step: setup storage
        self.scheduler.add_once("azure_formation", "setup_storage", context=sctx, seconds=0)
        return

    def setup_storage(self, sctx):
        # get context from super context
        # ctx = sctx.job_ctxs[sctx.current_job_index]

        self.log.debug("azure virtual environment %d storage setup done" % sctx.current_job_index)

        # next step: setup virtual machine
        self.scheduler.add_once("azure_formation", "setup_virtual_machine", context=sctx, seconds=0)

    def setup_virtual_machine(self, sctx):
        # get context from super context
        # ctx = sctx.job_ctxs[sctx.current_job_index]

        self.log.debug("azure virtual environment %d vm setup done" % sctx.current_job_index)

        # step to config next unit
        sctx.current_job_index += 1
        self.scheduler.add_once("azure_formation", "schedule_setup", context=sctx, seconds=0)
