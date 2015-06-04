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

from hackathon.database.models import (
    AzureKey,
    HackathonAzureKey,
    Hackathon,
)

from hackathon import RequiredFeature, Component
import os
import commands


class AzureCertManagement(Component):
    def __init__(self):
        self.CERT_BASE = self.util.get_config('azure.cert_base')
        self.CONTAINER_NAME = self.util.get_config('azure.container_name')
        self.file_service = RequiredFeature("file_service")

    def create_certificate(self, subscription_id, management_host, hackathon_name):
        """
        1. check certificate dir
        2. generate pem file
        3. generate cert file
        4. add azure key to db
        5. add hackathon azure key to db
        :param subscription_id:
        :param management_host:
        :param hackathon_name:
        :return:
        """

        # make sure certificate dir exists
        if not os.path.isdir(self.CERT_BASE):
            self.log.debug('certificate dir not exists')
            os.mkdir(self.CERT_BASE)

        base_url = '%s/%s' % (self.CERT_BASE, subscription_id)

        pem_url = base_url + '.pem'
        # avoid duplicate pem generation
        if not os.path.isfile(pem_url):
            pem_command = 'openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout %s -out %s -batch' % \
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
                                                 cert_url=cert_url,
                                                 pem_url=pem_url,
                                                 subscription_id=subscription_id,
                                                 management_host=management_host)
        # avoid duplicate azure key
        if azure_key is None:
            azure_key = self.db.add_object_kwargs(AzureKey,
                                                  cert_url=cert_url,
                                                  pem_url=pem_url,
                                                  subscription_id=subscription_id,
                                                  management_host=management_host)
            self.db.commit()
        else:
            self.log.debug('azure key exists')

        hackathon_id = self.db.find_first_object_by(Hackathon, name=hackathon_name).id
        hackathon_azure_key = self.db.find_first_object_by(HackathonAzureKey,
                                                           hackathon_id=hackathon_id,
                                                           azure_key_id=azure_key.id)
        # avoid duplicate hackathon azure key
        if hackathon_azure_key is None:
            self.db.add_object_kwargs(HackathonAzureKey,
                                      hackathon_id=hackathon_id,
                                      azure_key_id=azure_key.id)
            self.db.commit()
        else:
            self.log.debug('hackathon azure key exists')

        azure_cert_url = self.file_service.upload_file_to_azure_from_path(cert_url, self.CONTAINER_NAME,
                                                                          subscription_id + '.cer')
        azure_key.cert_url = azure_cert_url
        self.db.commit()
        return azure_cert_url


    def get_certificates(self, hackathon_name):
        hackathon_id = self.db.find_first_object_by(Hackathon, name=hackathon_name).id
        hackathon_azure_keys = self.db.find_all_objects_by(HackathonAzureKey, hackathon_id=hackathon_id)
        if hackathon_azure_keys is None:
            self.log.error('hackathon [%s] has no certificates' % hackathon_id)
            return None
        certificates = []
        for hackathon_azure_key in hackathon_azure_keys:
            dic = self.db.get_object(AzureKey, hackathon_azure_key.azure_key_id).dic()
            certificates.append(dic)
        return certificates

    def delete_certificate(self, certificate_id, hackathon_name):
        certificate_id = int(certificate_id)
        hackathon_id = self.db.find_first_object_by(Hackathon, name=hackathon_name).id
        hackathon_azure_keys = self.db.find_all_objects_by(HackathonAzureKey, hackathon_id=hackathon_id)
        if hackathon_azure_keys is None:
            self.log.error('hackathon [%d] has no certificates' % hackathon_id)
            return False
        azure_key_ids = map(lambda x: x.azure_key_id, hackathon_azure_keys)
        if certificate_id not in azure_key_ids:
            self.log.error('hackathon [%d] has no certificate [%d]' % (hackathon_id, certificate_id))
            return False
        self.db.delete_all_objects_by(HackathonAzureKey, hackathon_id=hackathon_id, azure_key_id=certificate_id)
        certificate = self.db.get_object(AzureKey, certificate_id)
        self.db.delete_object(certificate)
        self.db.commit()
        return True


# if __name__ == '__main__':
# azure_management = AzureManagement()
# cert_url = azure_management.create_certificate('guhr34nfj', 'fhdufew3', 'open-xml-sdk')
# print cert_url