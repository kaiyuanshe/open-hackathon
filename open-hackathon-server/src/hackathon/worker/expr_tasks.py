from hackathon.hmongo.models import Experiment, Hackathon
from hackathon.constants import EStatus
from hackathon import RequiredFeature

from . import celery_app as worker

template_library = RequiredFeature("template_library")


@worker.task(name="batch_start_expr")
def pre_alloc_expr(hackathon_id, template, count):
    template_content = template_library.load_template(template)
    hackathon = Hackathon.objects(id=hackathon_id).first()

    for i in range(count):
        expr = Experiment(status=EStatus.INIT,
                          template=template,
                          virtual_environments=[],
                          hackathon=hackathon)
        expr.save()
        start_new_expr.delay(hackathon_id, str(expr.id), template_content)


@worker.task(name="start_new_expr")
def start_new_expr(hackathon_id, expr_id, template_content):
    pass


@worker.task(name="stop_expr")
def stop_expr(hackathon_id, expr_id):
    pass


@worker.task(name="clean_resources")
def clean_resources(hackathon_id):
    pass
