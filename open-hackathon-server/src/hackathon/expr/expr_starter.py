# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import sys

sys.path.append("..")

from hackathon import Component, RequiredFeature, Context
from hackathon.hmongo.models import Experiment
from hackathon.constants import EStatus, VEStatus

__all__ = ["ExprStarter"]


class ExprStarter(Component):
    """Base for experiment starter"""

    template_library = RequiredFeature("template_library")

    def start_expr(self, context):
        """To start a new Experiment asynchronously

        :type context: Context
        :param context: the execution context.

        """
        expr = Experiment(status=EStatus.INIT,
                          template=context.template,
                          user=context.user,
                          virtual_environments=[],
                          hackathon=context.hackathon)
        expr.save()

        template_content = self.template_library.load_template(context.template)
        expr.status = EStatus.STARTING
        expr.save()

        # context contains complex object, we need create another serializable one with only simple fields
        new_context = Context(template_content=template_content,
                              template_name=context.template.name,
                              hackathon_id=context.hackathon.id,
                              experiment_id=expr.id)
        if context.get("user", None):
            new_context.user_id = context.user.id
        self._internal_start_expr(new_context)
        new_context.experiment = expr
        return new_context

    def stop_expr(self, context):
        """Stop experiment asynchronously

        :type context: Context
        :param context: the execution context.

        """
        return self._internal_stop_expr(context)

    def rollback(self, context):
        """cancel/rollback a expr which is in error state

        :type context: Context
        :param context: the execution context.

        """
        return self._internal_rollback(context)

    def _internal_start_expr(self, context):
        raise NotImplementedError()

    def _internal_stop_expr(self, context):
        raise NotImplementedError()

    def _internal_rollback(self, context):
        raise NotImplementedError()

    def _on_virtual_environment_failed(self, context):
        self.rollback(context)

    def _on_virtual_environment_success(self, context):
        expr = Experiment.objects(id=context.experiment_id).no_dereference() \
            .only("status", "virtual_environments").first()
        if all(ve.status == VEStatus.RUNNING for ve in expr.virtual_environments):
            expr.status = EStatus.RUNNING
            expr.save()
            self._on_expr_started(context)

        self._hooks_on_virtual_environment_success(context)

    def _on_virtual_environment_stopped(self, context):
        expr = Experiment.objects(id=context.experiment_id).no_dereference() \
            .only("status", "virtual_environments").first()
        ve = expr.virtual_environments.get(name=context.virtual_environment_name)
        ve.status = VEStatus.STOPPED

        if all(ve.status == VEStatus.STOPPED for ve in expr.virtual_environments):
            expr.status = EStatus.STOPPED
            expr.save()

    def _on_virtual_environment_unexpected_error(self, context):
        self.log.warn("experiment unexpected error: " + context.experiment_id)
        expr = Experiment.objects(id=context.experiment_id).no_dereference() \
            .only("status", "virtual_environments").first()
        if "virtual_environment_name" in context:
            expr.virtual_environments.get(name=context.virtual_environment_name).status = VEStatus.UNEXPECTED_ERROR
        expr.save()

    def _hooks_on_virtual_environment_success(self, context):
        pass

    def _on_expr_started(self, context):
        # send notice
        pass
