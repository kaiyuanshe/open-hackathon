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

from hackathon.hazure.cloud_service_adapter import CloudServiceAdapter
from hackathon.hmongo.models import Hackathon, AzureKey, Experiment

from hackathon import RequiredFeature, Component, Context, internal_server_error
from hackathon.hackathon_response import ok, bad_request
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
        cert_url = base_url + '.cer'

        # avoid duplicate pem generation
        if not os.path.isfile(pem_url):
            pem_command = 'openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout %s -out %s -batch' % \
                          (pem_url, pem_url)
            commands.getstatusoutput(pem_command)
        else:
            self.log.debug('%s exists' % pem_url)

        # avoid duplicate cert generation
        if not os.path.isfile(cert_url):
            cert_command = 'openssl x509 -inform pem -in %s -outform der -out %s' % (pem_url, cert_url)
            commands.getstatusoutput(cert_command)
        else:
            self.log.debug('%s exists' % cert_url)

        azure_key = AzureKey.objects(subscription_id=subscription_id, management_host=management_host).first()

        if azure_key is None:
            azure_key = AzureKey(
                cert_url=base_url + '.cer',
                pem_url=base_url + '.pem',
                subscription_id=subscription_id,
                management_host=management_host,
                verified=False
            )

            azure_key.save()

            hackathon.azure_keys.append(azure_key)
            hackathon.save()
        else:
            self.log.debug('azure key exists')

        if not (azure_key in hackathon.azure_keys):
            hackathon.azure_keys.append(azure_key)
            hackathon.save()
        else:
            self.log.debug('hackathon azure key exists')

        # store cer file
        cer_context = Context(
            hackathon_name=hackathon.name,
            file_name=subscription_id + '.cer',
            file_type=FILE_TYPE.AZURE_CERT,
            content=file(cert_url)
        )
        self.log.debug("saving cerf file [%s] to azure" % cer_context.file_name)
        cer_context = self.storage.save(cer_context)
        azure_key.cert_url = cer_context.url

        # store pem file
        # encrypt certification file before upload to storage
        encrypted_pem_url = self.__encrypt_content(pem_url)
        pem_contex = Context(
            hackathon_name=hackathon.name,
            file_name=subscription_id + '.pem',
            file_type=FILE_TYPE.AZURE_CERT,
            content=file(encrypted_pem_url)
        )
        self.log.debug("saving pem file [%s] to azure" % pem_contex.file_name)
        pem_contex = self.storage.save(pem_contex)
        os.remove(encrypted_pem_url)
        azure_key.pem_url = pem_contex.url

        azure_key.save()

        return azure_key.dic()

    def get_certificates_by_expr(self, expr_id):
        """Get certificates by experiment id
        """
        # expr = self.db.get_object(Experiment, expr_id)
        expr = Experiment.objects(id=expr_id)
        # hak = self.db.find_all_objects_by(HackathonAzureKey, hackathon_id=expr.hackathon_id)
        hak = Hackathon.objects(id=expr.hackathon_id).first().azure_keys[0]
        if not hak:
            raise Exception("no azure key configured")

        return map(lambda key: self.db.get_object(AzureKey, key.azure_key_id), hak)

    def get_certificates(self, hackathon):
        """Get certificates by hackathon

        :type hackathon: Hackathon
        :param hackathon: instance of hackathon to search certificates

        :rtype list
        :return a list of AzureKey
        """

        hackathon_azure_keys = [a.dic() for a in hackathon.azure_keys]

        if len(hackathon_azure_keys) == 0:
            # if no certificates added before, return 404
            return []

        return hackathon_azure_keys

    def delete_certificate(self, certificate_id, hackathon):
        """Delete certificate by azureKey.id and hackathon

        Delete the hackathon-azureKey relationship first. If the auzreKey is not needed any more, delete the azureKey too

        :type certificate_id: int
        :param certificate_id: id of AzureKey

        :type hackathon: Hackathon
        :param hackathon: instance of Hackathon
        """
        # delete all hackathon-azureKey relationships first

        azure_key = AzureKey.objects(id=certificate_id).first()

        # if no relations left, delete the azureKey itself
        if azure_key in hackathon.azure_keys:
            try:
                if isfile(azure_key.cert_url):
                    os.remove(azure_key.cert_url)
                else:
                    self.storage.delete(azure_key.cert_url)
                if isfile(azure_key.pem_url):
                    os.remove(azure_key.pem_url)
                else:
                    self.storage.delete(azure_key.pem_url)
            except Exception as e:
                self.log.error(e)

            hackathon.azure_keys.remove(azure_key)
            hackathon.save()

        return ok(True)

    def check_sub_id(self, subscription_id):

        azure_key = AzureKey.objects(subscription_id=subscription_id).first()

        if self.util.is_local():
            if azure_key is not None:
                azure_key.verified = True
                azure_key.save()
            return ok("success")

        if azure_key is None:
            return internal_server_error("No available azure key on the server side.")

        sms = CloudServiceAdapter(azure_key.subscription_id,
                                  azure_key.get_local_pem_url(),
                                  host=azure_key.management_host)
        if sms.ping():
            azure_key.verified = True
            azure_key.save()
        else:
            return bad_request("Subscription id is not valid, check whether subscription id is valid and upload the right cer file to azure")

        return ok("success")

    def __init__(self):
        self.CERT_BASE = self.util.get_config('azure.cert_base')
        self.__ensure_certificates_dir()

    def __ensure_certificates_dir(self):
        """Ensure that the directory to store azure certificate exists"""
        if not self.CERT_BASE:
            self.CERT_BASE = abspath("%s/../certificates" % dirname(realpath(__file__)))

        if not os.path.exists(self.CERT_BASE):
            os.makedirs(self.CERT_BASE)

    def __encrypt_content(self, pem_url):
        encrypted_pem_url = pem_url + ".encrypted"
        cryptor = RequiredFeature("cryptor")
        cryptor.encrypt(pem_url, encrypted_pem_url)
        return encrypted_pem_url

    def get_local_pem_url(self, pem_url):
        local_pem_url = self.CERT_BASE + "/" + pem_url.split("/")[-1]
        if not isfile(local_pem_url):
            self.log.debug("Recover local %s.pem file from azure storage %s" % (local_pem_url, pem_url))
            cryptor = RequiredFeature("cryptor")
            cryptor.recover_local_file(pem_url, local_pem_url)
        return local_pem_url


# recover a pem file from azure
def get_local_pem_url(azureKey):
    azure_cert_manager = RequiredFeature("azure_cert_manager")
    return azure_cert_manager.get_local_pem_url(azureKey.pem_url)


AzureKey.get_local_pem_url = get_local_pem_url
