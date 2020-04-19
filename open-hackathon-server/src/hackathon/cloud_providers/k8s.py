from .util import BaseProvider


class K8sProvider(BaseProvider):
    def connect(self):
        pass

    def create_instance(self, ins_cfg):
        pass

    def start_instance(self, ins_cfg):
        pass

    def pause_instance(self, ins_cfg):
        pass

    def delete_instance(self, ins_cfg):
        pass
