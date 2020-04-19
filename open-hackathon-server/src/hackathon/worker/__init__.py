import os
import logging
from celery import Celery, Task

from hackathon.util import safe_get_config

LOG = logging.getLogger(__name__)

celery_always_eager = os.getenv("DEBUG", "false") == "true"
LOG.debug("Create celery app and celery_always_eager is {}".format(
    celery_always_eager))


class OhpTask(Task):
    def run(self, *args, **kwargs):
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(OhpTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        super(OhpTask, self).on_success(retval, task_id, args, kwargs)


celery_app = Celery(
    "ohp_worker",
    include=[
        "worker.expr_tasks",
    ],
    task_cls=OhpTask)
celery_app.conf.update(
    CELERY_BROKER_URL=safe_get_config("CELERY_BROKER_URL", ""),
    CELERY_RESULT_BACKEND=safe_get_config("CELERY_RESULT_BACKEND", ""),
    CELERY_DEFAULT_EXCHANGE='ohp',
    CELERYD_CONCURRENCY=20,
    CELERYD_MAX_TASKS_PER_CHILD=50,
    CELERY_DEFAULT_QUEUE='ohp.tasks.queue',
    CELERY_DEFAULT_ROUTING_KEY='ohp.tasks',
    CELERY_ALWAYS_EAGER=celery_always_eager,
    CELERY_TASK_ALWAYS_EAGER=celery_always_eager,
)
