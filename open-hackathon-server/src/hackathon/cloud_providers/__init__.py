import time
import random
import string
import logging

from hackathon.hmongo.models import K8sEnvironment, VirtualEnvironment
from hackathon.constants import VE_PROVIDER, EStatus, VEStatus, VERemoteProvider

__all__ = ["Provider", "ProviderError"]

LOG = logging.getLogger(__name__)

_provider_classes = {}


class ProviderError(Exception):
    pass


class Provider:
    def __init__(self, provider_type, provider_cfg):
        if provider_type not in _provider_classes:
            raise ProviderError("{} provider not found", provider_type)
        self.provider_type = provider_type
        self.p_class = _provider_classes[provider_type]
        self.p = self.p_class(provider_cfg)

        try:
            self.p.connect()
        except Exception as e:
            raise ProviderError("connect Provider Platform error: {}".format(e))

    def create_expr(self, experiment, template_content):
        LOG.info("creating experiment {}".format(experiment.id))
        start_at = time.time()
        experiment.status = EStatus.STARTING
        experiment.save()

        try:
            new_env = self.p.create_instance(self._get_ve_config(experiment, template_content))
            experiment.virtual_environments[0] = new_env
            experiment.save()

            self.wait_for_ready()
        except Exception as e:
            LOG.error("wait for start error: {}".format(e))
            experiment.status = EStatus.FAILED
        else:
            experiment.virtual_environments[0].status = VEStatus.RUNNING
            experiment.status = EStatus.RUNNING
        experiment.save()
        LOG.info("create expr spend time: {}".format(time.time() - start_at))

    def start_expr(self, experiment):
        # TODO
        pass

    def pause_expr(self, experiment):
        # TODO
        pass

    def delete_expr(self, experiment):
        LOG.info("deleting experiment {}".format(experiment.id))

        try:
            self.p.delete_instance(experiment.virtual_environments[0])
        except Exception as e:
            LOG.error("delete expr error: {}".format(e))
            experiment.status = EStatus.FAILED
        else:
            experiment.status = EStatus.STOPPED
        experiment.save()
        LOG.info("experiment {} deleted".format(experiment.id))

    def wait_for_ready(self):
        self.p.wait_instance_ready()

    def get_remote_config(self):
        pass

    def _get_ve_config(self, experiment, template_content):
        if not experiment.virtual_environments or len(experiment.virtual_environments) == 0:
            experiment.virtual_environments = [self._init_ve_config(experiment, template_content)]
            experiment.save()

        return experiment.virtual_environments[0]

    def _init_ve_config(self, experiment, template_content):
        if self.provider_type == VE_PROVIDER.K8S:
            hackathon = experiment.hackathon
            unit = template_content.unit
            env_name = "{}-{}".format(hackathon.name, "".join(random.sample(string.ascii_lowercase, 6)))
            yaml_content = unit.gen_k8s_yaml(env_name)
            k8s_env = K8sEnvironment.load_from_yaml(env_name, yaml_content)
            return VirtualEnvironment(
                provider=VE_PROVIDER.K8S,
                name=env_name,
                status=VEStatus.INIT,
                remote_provider=VERemoteProvider.Guacamole,
                k8s_resource=k8s_env,
            )
        raise ProviderError("not found {} instance config".format(self.provider_type))


def register_provider(provider_type, provider_class):
    _provider_classes[provider_type] = provider_class


def _register():
    from .k8s import K8sProvider
    register_provider(VE_PROVIDER.K8S, K8sProvider)


_register()
