import re
import yaml as yaml_util
from yaml.parser import ParserError

from .errors import YmlParseError

RESOURCE_NAME_PATTERN = re.compile(
    r'[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*')
SERVICE_NAME_PATTERN = re.compile(r'[a-z]([-a-z0-9]*[a-z0-9])?')


class YamlBuilder(object):
    def __init__(self, images, ports, namespace, **kwargs):
        self.deploy_yamls = []
        self.svc_yamls = []
        self.namespace = namespace

        self.images = images
        self.ports = ports
        self.config = kwargs

    def create_deployment(self):
        pass

    def create_service(self):
        pass

    def build(self):
        pass

    def get_yaml(self):
        return yaml_util.dump_all(self.deploy_yamls + self.svc_yamls)
