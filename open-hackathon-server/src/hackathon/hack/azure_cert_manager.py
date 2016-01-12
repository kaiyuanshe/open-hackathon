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

sys.path.append('..')

import os
from os.path import dirname, realpath, abspath, isfile
import commands

from hackathon.database import AzureKey, HackathonAzureKey, Hackathon
from hackathon import RequiredFeature, Component, Context
from hackathon.hackathon_response import not_found, ok
from hackathon.constants import FILE_TYPE

__all__ = ["AzureCertManager"]


class AzureCertManager(Component):
    """Manage azure/mooncake certificates for the hackathon

    Note that certificate is actually certificate pair: a cer file and a pem file.
    The cer file is for user to download from our site and then upload to the azure/mooncake account.
    The pem file is for azure python SDK. Everytime request from OHP to azure should include the pem cert.

    cer file will be saved in different places according to the implementation of storage. But pem file will be saved
    """

    storage = RequiredFeature("storage")

    def create_certificate(self, subscription_id, management_host, hackathon):
        """Create certificate for specific subscription and hackathon

        1. check certificate dir
        2. generate pem file
        3. generate cert file
        4. add azure key to db
        5. add hackathon azure key to db
        :param subscription_id:
        :param management_host:
        :param hackathon:
        :return:
        """

        base_url = '%s/%s' % (self.CERT_BASE, subscription_id)
        pem_url = base_url + '.pem'

        # avoid duplicate pem generation
        if not os.path.isfile(pem_url):
            pem_command = 'openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout %s -out %s -batch' % \
                          (pem_url, pem_url)
            commands.getstatusoutput(pem_command)
        else:
            self.log.debug('%s exists' % pem_url)

        cert_url = base_url + '.cer'
        # avoid duplicate cert generation
        if not os.path.isfile(cert_url):
            cert_command = 'openssl x509 -inform pem -in %s -outform der -out %s' % (pem_url, cert_url)
            commands.getstatusoutput(cert_command)
        else:
            self.log.debug('%s exists' % cert_url)

        azure_key = self.db.find_first_object_by(AzureKey,
                                                 subscription_id=subscription_id,
                                                 management_host=management_host)
        # avoid duplicate azure key
        if azure_key is None:
            azure_key = self.db.add_object_kwargs(AzureKey,
                                                  cert_url=cert_url,
                                                  pem_url=pem_url,
                                                  azure_pem_url=pem_url,
                                                  subscription_id=subscription_id,
                                                  management_host=management_host)
            self.db.commit()
        else:
            self.log.debug('azure key exists')

        hackathon_azure_key = self.db.find_first_object_by(HackathonAzureKey,
                                                           hackathon_id=hackathon.id,
                                                           azure_key_id=azure_key.id)
        # avoid duplicate hackathon azure key
        if hackathon_azure_key is None:
            self.db.add_object_kwargs(HackathonAzureKey,
                                      hackathon_id=hackathon.id,
                                      azure_key_id=azure_key.id)
            self.db.commit()
        else:
            self.log.debug('hackathon azure key exists')

        cer_file_name = subscription_id + '.cer'
        cer_context = Context(
            hackathon_name=hackathon.name,
            file_name=cer_file_name,
            file_type=FILE_TYPE.AZURE_CERT,
            content=file(cert_url)
        )
        self.log.debug("saving cerf file [%s] to azure" % cer_file_name)
        cer_context = self.storage.save(cer_context)
        azure_key.cert_url = cer_context.url
        self.db.commit()

        # store pem file
        pem_file_name = subscription_id + '.pem'
        pem_contex = Context(
            hackathon_name=hackathon.name,
            file_name=pem_file_name,
            file_type=FILE_TYPE.AZURE_PEM,
            content=file(pem_url)
        )
        self.log.debug("saving pem file [%s] to azure" % pem_file_name)
        pem_contex = self.storage.save(pem_contex)
        azure_key.azure_pem_url = pem_contex.url
        self.db.commit()
        return azure_key.cert_url

    def get_certificates(self, hackathon):
        """Get certificates by hackathon

        :type hackathon: Hackathon
        :param hackathon: instance of hackathon to search certificates

        :rtype list
        :return a list of AzureKey
        """
        hackathon_azure_keys = self.db.find_all_objects_by(HackathonAzureKey, hackathon_id=hackathon.id)
        if len(hackathon_azure_keys) == 0:
            # if no certificates added before, return 404
            return []

        certificates = map(lambda key: self.db.get_object(AzureKey, key.azure_key_id).dic(),
                           hackathon_azure_keys)
        return certificates

    def delete_certificate(self, certificate_id, hackathon):
        """Delete certificate by azureKey.id and hackathon

        Delete the hackathon-azureKey relationship first. If the auzreKey is not needed any more, delete the azureKey too

        :type certificate_id: int
        :param certificate_id: id of AzureKey

        :type hackathon: Hackathon
        :param hackathon: instance of Hackathon
        """
        # delete all hackathon-azureKey relationships first
        self.db.delete_all_objects_by(HackathonAzureKey, hackathon_id=hackathon.id, azure_key_id=certificate_id)

        # if no relations left, delete the azureKey itself
        if self.db.count_by(HackathonAzureKey, azure_key_id=certificate_id) == 0:
            azure_key = self.db.get_object(AzureKey, certificate_id)
            if azure_key:
                try:
                    if isfile(azure_key.cert_url):
                        os.remove(azure_key.cert_url)
                    else:
                        self.storage.delete(azure_key.cert_url)
                    if isfile(azure_key.azure_pem_url):
                        os.remove(azure_key.azure_pem_url)
                    else:
                        self.storage.delete(azure_key.azure_pem_url)
                except Exception as e:
                    self.log.error(e)

                self.db.delete_all_objects_by(AzureKey, id=certificate_id)
                self.db.commit()

        return ok()

    def __init__(self):
        self.CERT_BASE = self.util.get_config('azure.cert_base')
        self.__ensure_certificates_dir()

    def __ensure_certificates_dir(self):
        """Ensure that the directory to store azure certificate exists"""
        if not self.CERT_BASE:
            self.CERT_BASE = abspath("%s/../certificates" % dirname(realpath(__file__)))

        if not os.path.exists(self.CERT_BASE):
            os.makedirs(self.CERT_BASE)