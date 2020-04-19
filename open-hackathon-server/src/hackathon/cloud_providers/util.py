import abc
from collections import namedtuple


class BaseProvider(abc.ABC):
    def __init__(self, cfg):
        self.cfg = cfg

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def create_instance(self, ins_cfg):
        pass

    @abc.abstractmethod
    def start_instance(self, ins_cfg):
        pass

    @abc.abstractmethod
    def pause_instance(self, ins_cfg):
        pass

    @abc.abstractmethod
    def delete_instance(self, ins_cfg):
        pass

    @abc.abstractmethod
    def wait_instance_ready(self, ins_cfg, timeout=None):
        pass


Instance = namedtuple("Instance", field_names=[])
