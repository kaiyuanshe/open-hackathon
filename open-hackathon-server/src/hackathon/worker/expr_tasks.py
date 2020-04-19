from hackathon.hmongo.models import Experiment, Hackathon
from hackathon.constants import EStatus
from hackathon import RequiredFeature

from . import celery_app as worker

template_library = RequiredFeature("template_library")


@worker.task(name="start_new_expr")
def start_new_expr(hackathon_id, expr_id, template_content):
    pass


@worker.task(name="stop_expr")
def stop_expr(hackathon_id, expr_id):
    pass


@worker.task(name="clean_resources")
def clean_resources(hackathon_id):
    pass
