__author__ = 'root'
import database
import log
from remotedocker import *


class RollBack(object):
    def __init__(self):
        pass

    def reset_expr_status(self, expr_id):
        docker = RemoteDocker()
        expr = Experiment.query.filter_by(id=expr_id, status=1).first()
        if expr is not None:
            for c in expr.containers:
                try:
                    docker.stop(c.name, c.host_server.public_dns)
                    c.status = 2
                    c.host_server.container_count -= 1
                    if c.host_server.container_count < 0:
                        c.host_server.container_count = 0
                    db.session.commit()
                except Exception as e:
                    log.error(e)
                    expr.status = 4
                    db.session.commit()

            expr.status = 2
            db.session.commit()

        return "OK"
