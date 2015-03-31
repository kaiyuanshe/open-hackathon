__author__ = 'Yifu Huang'

import sys

sys.path.append("..")

from azureImpl import *
from hackathon.functions import *
from hackathon.enum import *


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