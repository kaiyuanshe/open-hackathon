import logging
from mongoengine import Q

from hackathon import RequiredFeature
from hackathon.hmongo.models import Experiment, Hackathon
from hackathon.template.template_content import TemplateContent
from hackathon.cloud_providers import Provider, ProviderError
from hackathon.constants import HACK_STATUS, HACKATHON_CONFIG, EStatus

from . import celery_app as worker
from .expr_tasks import start_new_expr

LOG = logging.getLogger(__name__)

expr_manager = RequiredFeature("expr_manager")


@worker.task(name="check_and_pre_allocate_expr")
def check_and_pre_allocate_expr():
    hackathon_list = Hackathon.objects(status=HACK_STATUS.ONLINE)
    for hack in hackathon_list:
        if not hack.enable_pre_allocate:
            continue

        LOG.debug("add pre_allocate job for hackathon %s" % str(hack.name))
        pre_allocate_expr.delay(str(hack.id))


@worker.task(name="pre_allocate_expr")
def pre_allocate_expr(hackathon_id):
    LOG.info("pre_allocate_expr for hackathon {}".format(hackathon_id))
    hackathon = Hackathon.objects(id=hackathon_id).first()
    if not hackathon:
        LOG.error("pre_allocate_expr without hackathon")
        return
    if not hackathon.templates or len(hackathon.templates) == 0:
        LOG.error("hackathon has no template")

    template = hackathon.templates[0]
    pre_num = int(hackathon.config.get(HACKATHON_CONFIG.PRE_ALLOCATE_NUMBER, 1))
    query = Q(status=EStatus.STARTING) | Q(status=EStatus.RUNNING)
    curr_num = Experiment.objects(user=None, hackathon=hackathon, template=template).filter(query).count()

    if curr_num >= pre_num:
        LOG.info("start 0 expr, finish")
        return

    try_create = expr_manager.start_pre_alloc_exprs(template.name, hackathon.name, pre_num - curr_num)
    LOG.info("start {} expr, finish".format(try_create))
