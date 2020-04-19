import logging

from hackathon import RequiredFeature
from hackathon.hmongo.models import Experiment, Hackathon
from hackathon.template.template_content import TemplateContent
from hackathon.cloud_providers import Provider, ProviderError

from . import celery_app as worker

template_library = RequiredFeature("template_library")
LOG = logging.getLogger(__name__)


@worker.task(name="start_new_expr")
def start_new_expr(hackathon_id, expr_id, template_content):
    hackathon = Hackathon.objects(id=hackathon_id).first()
    if not hackathon:
        LOG.error("start new expr without hackathon")
    experiment = Experiment.objects(id=expr_id).first()
    if not experiment:
        LOG.error("start new expr without experiment")

    if hackathon.templates is None or len(hackathon.templates) == 0:
        LOG.error("start new expr without template")

    unit = template_content.unit
    provider = _try_connect(unit.provider, template_content.provider_cfg)
    if not provider:
        return

    provider.create_expr(experiment, template_content)

    # todo init Guacamole config
    _ = provider.get_remote_config()


@worker.task(name="stop_expr")
def stop_expr(hackathon_id, expr_id):
    hackathon = Hackathon.objects(id=hackathon_id).first()
    if not hackathon:
        LOG.error("stop expr without hackathon")
    experiment = Experiment.objects(id=expr_id).first()
    if not experiment:
        LOG.error("stop expr without experiment")

    template = experiment.template
    template_content = TemplateContent.load_from_template(template)
    unit = template_content.unit
    provider = _try_connect(unit.provider, template_content.provider_cfg)
    if not provider:
        return

    provider.delete_expr(experiment)


def _try_connect(provider, provider_cfg):
    try:
        return Provider(provider, provider_cfg)
    except ProviderError as e:
        LOG.error("init provider error: {}".format(e))
    return None
