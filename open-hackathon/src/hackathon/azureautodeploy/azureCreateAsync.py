# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#  
# The MIT License (MIT)
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#  
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

__author__ = 'Yifu Huang'

import sys

sys.path.append("..")

from azureImpl import *
from hackathon.functions import *
from hackathon.enum import *
from hackathon.hack import hack_manager


def set_expr_status(e_id, status):
    expr = db_adapter.get_object(Experiment, e_id)
    expr.status = status
    db_adapter.commit()


if __name__ == "__main__":
    args = sys.argv[1:]
    ut_id = int(args[0])
    expr_id = int(args[1])
    azure = AzureImpl()
    sub_id = get_config("azure.subscriptionId")
    cert_path = get_config('azure.certPath')
    service_host_base = get_config("azure.managementServiceHostBase")
    if not azure.connect(sub_id, cert_path, service_host_base):
        set_expr_status(expr_id, ExprStatus.Failed)
        sys.exit(-1)
    template = db_adapter.get_object(Template, ut_id)
    try:
        result = azure.create_sync(template, expr_id)
    except Exception as e:
        log.error(e)
        set_expr_status(expr_id, ExprStatus.Failed)
        sys.exit(-1)
    if not result:
        set_expr_status(expr_id, ExprStatus.Failed)
        sys.exit(-1)
    set_expr_status(expr_id, ExprStatus.Running)
    hack_manager.increase_win10_trial_count()