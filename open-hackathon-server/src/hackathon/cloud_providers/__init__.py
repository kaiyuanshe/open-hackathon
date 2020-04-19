__all__ = ["Provider"]

_provider_classes = {}


class Provider:
    def __init__(self, name, provider_cfg):
        self.p_class = _provider_classes[name]
        self.p = self.p_class(provider_cfg)

        self.p.connect()

    def create_expr(self, hackathon, experiment, template_content):
        pass

    def start_expr(self, hackathon, experiment, template_content):
        # TODO
        pass

    def pause_expr(self, hackathon, experiment, template_content):
        # TODO
        pass

    def delete_expr(self, hackathon, experiment, template_content):
        pass

    def wait_for_ready(self):
        pass


def registry_provider(name, provider):
    _provider_classes[name] = provider
