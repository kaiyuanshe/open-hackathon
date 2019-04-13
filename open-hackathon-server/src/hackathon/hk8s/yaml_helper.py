import re
from copy import deepcopy

from hackathon.template.template_constants import K8S_UNIT

from .errors import YmlParseError

RESOURCE_NAME_PATTERN = re.compile(r'[a-z]([-a-z0-9]*[a-z0-9])?')
DEPLOYMENT_TEMPLATE = {
    'apiVersion': 'apps/v1',
    'kind': 'Deployment',
    'metadata': {
        'labels': {},
        'name': '',
        'namespace': '',
    },
    'spec': {
        'replicas': 1,
        'selector': {'matchLabels': {'env': ''}},
        'template': {
            'metadata': {'labels': {'env': ''}},
            'spec': {
                'containers': []}
        }
    }
}
SERVICE_TEMPLATE = {
    'apiVersion': 'v1',
    'kind': 'Service',
    'metadata': {'name': '', 'namespace': '', 'labels': {}},
    'spec': {
        'ports': [],
        'selector': {'env': ''},
        'type': 'NodePort'
    }
}


class YamlBuilder(object):
    def __init__(self, env_name, template_unit, labels):
        self.deploy_name = str(env_name).lower()
        self.deploy_yamls = deepcopy(DEPLOYMENT_TEMPLATE)
        self.svc_yamls = deepcopy(SERVICE_TEMPLATE)
        self.namespace = template_unit
        self.labels = {}
        for k, v in labels.items():
            self.labels[str(k)] = str(v)

        m = RESOURCE_NAME_PATTERN.match(self.deploy_name)
        if not m or m.group() != self.deploy_name:
            raise YmlParseError("Deployment name Cannot be used as a K8s resource name")

        self.cluster = template_unit.get_cluster()
        self.namespace = self.cluster[K8S_UNIT.CONFIG_NAMESPACES]
        self.images = template_unit.get_images()
        self.ports = template_unit.get_ports()
        self.resources = template_unit.get_resources()

    def build(self):
        env_name = self.deploy_name
        self.labels['env'] = env_name
        deployment_name = self.deploy_name
        service_name = deployment_name

        # Gen Deployment
        d_metadata = self.deploy_yamls['metadata']
        d_metadata['labels'].update(self.labels)
        d_metadata['name'] = deployment_name
        d_metadata['namespace'] = self.namespace

        spec = self.deploy_yamls['spec']
        spec['selector']['matchLabels']['env'] = env_name

        template = spec['template']
        p_metadata = template['metadata']
        assert isinstance(p_metadata, dict), "Pod metadata not a dict"
        p_metadata['labels'].update(self.labels)
        p_metadata['name'] = self.deploy_name

        containers = []
        _requests = self.resources[K8S_UNIT.RESOURCES_REQUESTS]
        _limits = self.resources[K8S_UNIT.RESOURCES_LIMITS]
        _count = 0
        for i in self.images:
            image = i[K8S_UNIT.IMAGES_IMAGE]
            containers.append({
                'image': image,
                'name': "{}-{}".format(self.deploy_name, _count),
                'resources': {
                    'limits': {
                        'cpu': str(_limits[K8S_UNIT.RESOURCES_LIMITS_CPU]),
                        'memory': str(_limits[K8S_UNIT.RESOURCES_LIMITS_MEM]),
                    },
                    'requests': {
                        'cpu': str(_requests[K8S_UNIT.RESOURCES_REQUESTS_CPU]),
                        'memory': str(_requests[K8S_UNIT.RESOURCES_REQUESTS_MEM]),
                    }
                }
            })
        template['spec']['containers'] = containers

        # Gen Service
        s_metadata = self.svc_yamls['metadata']
        s_metadata['name'] = service_name
        s_metadata['namespace'] = self.namespace
        s_metadata['labels'].update(self.labels)

        spec = self.svc_yamls['spec']
        assert isinstance(spec, dict)
        spec['selector']['env'] = env_name
        ports = []
        for p in self.ports:
            if not p[K8S_UNIT.PORTS_PUBLIC]:
                continue
            ports.append({
                'nodePort': int(p[K8S_UNIT.PORTS_PUBLIC_PORT]),
                'port': int(p[K8S_UNIT.PORTS_PORT]),
                'protocol': str(p[K8S_UNIT.PORTS_PROTOCOL]).upper(),
            })
        spec['ports'] = ports

    def get_deployment(self):
        return self.deploy_yamls

    def get_service(self):
        return self.svc_yamls
