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
__author__ = 'Yifu Huang'

from hackathon.log import (
    log,
)


class Subscription:
    """
    Subscription of azure resources according to given subscription id
    """
    ERROR_RESULT = -1

    def __init__(self, service):
        self.service = service

    def get_available_storage_account_count(self):
        """
        Get available count of storage account
        Return -1 if failed
        :return:
        """
        try:
            result = self.service.get_subscription()
        except Exception as e:
            log.error(e)
            return self.ERROR_RESULT
        return result.max_storage_accounts - result.current_storage_accounts

    def get_available_cloud_service_count(self):
        """
        Get available count of cloud service
        Return -1 if failed
        :return:
        """
        try:
            result = self.service.get_subscription()
        except Exception as e:
            log.error(e)
            return self.ERROR_RESULT
        return result.max_hosted_services - result.current_hosted_services

    def get_available_core_count(self):
        """
        Get available count of core
        Return -1 if failed
        :return:
        """
        try:
            result = self.service.get_subscription()
        except Exception as e:
            log.error(e)
            return self.ERROR_RESULT
        return result.max_core_count - result.current_core_count
