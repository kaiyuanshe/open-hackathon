import time
import logging
import yaml as yaml_tool
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning, HTTPError
from kubernetes import client
from kubernetes.client.rest import ApiException

from hackathon.constants import HEALTH, HEALTH_STATUS, K8S_DEPLOYMENT_STATUS

from .util import BaseProvider

LOG = logging.getLogger(__name__)
DEFAULT_CONNECT_TIMEOUT = 60
DEFAULT_RESYNC_TIME = 10

# 忽略自签名 ca 的告警日志
disable_warnings(InsecureRequestWarning)


class K8sResourceError(Exception):
    err_id = ""
    err_msg_format = "{}: {}"

    def __init__(self, err_msg):
        self._err_msg = err_msg

    @property
    def err_msg(self):
        return self.err_msg_format.format(self.err_id, self._err_msg)


class YmlParseError(K8sResourceError):
    err_id = "K8s Yaml parse error"


class EnvError(K8sResourceError):
    err_id = "K8s environment error"


class DeploymentError(EnvError):
    err_id = "K8s deployment error"


class ServiceError(EnvError):
    err_id = "K8s service error"


class StatefulSetError(EnvError):
    err_id = "K8s StatefulSet error"


class PVCError(EnvError):
    err_id = "K8s PersistentVolumeClaims error"


class K8sProvider(BaseProvider):
    def __init__(self, cfg):
        super(K8sProvider, self).__init__(cfg)

        self.namespace = cfg['namespace']
        self.api_url = cfg['api_url']
        self.token = cfg['token']

        configuration = client.Configuration()
        configuration.host = self.api_url
        configuration.api_key['authorization'] = 'bearer ' + self.token

        # TODO support ca
        configuration.verify_ssl = False
        self.configuration = configuration

        self.api_client = None

    def connect(self, timeout=DEFAULT_CONNECT_TIMEOUT):
        report = self.report_health(timeout)
        return report[HEALTH.STATUS] == HEALTH_STATUS.OK

    def report_health(self, timeout=20):
        try:
            api_instance = client.CoreV1Api(self.api_client)
            api_instance.list_namespaced_pod(self.namespace, timeout_seconds=timeout)
            return {HEALTH.STATUS: HEALTH_STATUS.OK}
        except ApiException as e:
            LOG.error("connect k8s api server error: {}".format(e))
            return {
                HEALTH.STATUS: HEALTH_STATUS.ERROR,
                HEALTH.DESCRIPTION: "Get Pod info error: {}".format(e),
            }
        except HTTPError:
            return {
                HEALTH.STATUS: HEALTH_STATUS.ERROR,
                HEALTH.DESCRIPTION: "Connect K8s ApiServer {} error: connection timeout".format(self.api_url),
            }

    def create_instance(self, ve_cfg):
        ins_cfg = ve_cfg.k8s_resource
        try:
            for pvc in ins_cfg.persistent_volume_claims:
                self.create_k8s_pvc(pvc)

            for i, s in enumerate(ins_cfg.services):
                svc_name = self.create_k8s_service(s)
                # overwrite service config and get the public port from K8s
                ins_cfg.services[i] = yaml_tool.dump(self.get_service_by_name(svc_name))

            for d in ins_cfg.deployments:
                self.create_k8s_deployment(d)

            for s in ins_cfg.stateful_sets:
                self.create_k8s_statefulset(s)
        except Exception as e:
            LOG.error("k8s_service_start_failed: {}".format(e))
        return ins_cfg

    def start_instance(self, ve_cfg):
        # TODO
        pass

    def pause_instance(self, ve_cfg):
        # TODO
        pass

    def delete_instance(self, ve_cfg):
        ins_cfg = ve_cfg.k8s_resource
        for d in ins_cfg.deployments:
            self.delete_k8s_deployment(d['metadata']['name'])

        for pvc in ins_cfg.persistent_volume_claims:
            self.delete_k8s_pvc(pvc['metadata']['name'])

        for s in ins_cfg.stateful_sets:
            self.delete_k8s_statefulset(s['metadata']['name'])

        for s in ins_cfg.services:
            self.delete_k8s_service(s['metadata']['name'])

    def wait_instance_ready(self, ve_cfg, timeout=None):
        ins_cfg = ve_cfg.k8s_resource
        start_at = time.time()
        while True:
            all_ready = True
            for d in ins_cfg.deployments:
                if all_ready and self.get_deployment_status(d['metadata']['name']) != K8S_DEPLOYMENT_STATUS.AVAILABLE:
                    all_ready = False
                    continue

            for s in ins_cfg.stateful_sets:
                # TODO check statfulSet status
                pass

            if all_ready:
                return all_ready

            time.sleep(DEFAULT_RESYNC_TIME)
            if timeout is not None and time.time() > start_at + timeout:
                raise RuntimeError("Start deployment error: Timeout")

    ###
    # Deployment
    ###

    def list_deployments(self, labels=None, timeout=20):
        _deployments = []
        kwargs = {"timeout_seconds": timeout, "watch": False}
        if labels and isinstance(labels, dict):
            label_selector = ",".join(["{}={}".format(k, v) for k, v in list(labels.items())])
            kwargs['label_selector'] = label_selector

        apps_v1_group = client.AppsV1Api(self.api_client)
        try:
            ret = apps_v1_group.list_namespaced_deployment(self.namespace, **kwargs)
        except ApiException as e:
            LOG.error(e)
            return []

        for i in ret.items:
            _deployments.append(i.metadata.name)
        return _deployments

    def deployment_exists(self, name):
        return self.get_deployment_by_name(name, need_raise=False) is not None

    def create_k8s_deployment(self, yaml):
        api_instance = client.AppsV1Api(self.api_client)
        if isinstance(yaml, str) or isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.safe_load(yaml)
        assert isinstance(yaml, dict), "Start a deployment without legal yaml."
        metadata = yaml.get("metadata", {})
        deploy_name = metadata.get("name")

        try:
            if self.get_deployment_by_name(deploy_name, need_raise=False):
                raise DeploymentError("Deployment name was existed.")

            api_instance.create_namespaced_deployment(self.namespace, yaml, async_req=False)
        except ApiException as e:
            LOG.error("Start deployment error: {}".format(e))
            raise DeploymentError("Start deployment error: {}".format(e))
        return deploy_name

    def get_deployment_by_name(self, deployment_name, need_raise=True):
        api_instance = client.AppsV1Api(self.api_client)
        try:
            _deploy = api_instance.read_namespaced_deployment(deployment_name, self.namespace)
        except ApiException:
            if need_raise:
                raise DeploymentError("Deplotment {} not found".format(deployment_name))
            return None
        return _deploy

    def get_deployment_status(self, deployment_name):
        _deploy = self.get_deployment_by_name(deployment_name)
        _status = _deploy.status
        if not _status.replicas:
            return K8S_DEPLOYMENT_STATUS.PAUSE
        if _status.replicas == _status.available_replicas:
            return K8S_DEPLOYMENT_STATUS.AVAILABLE
        if _status.unavailable_replicas > 0:
            return K8S_DEPLOYMENT_STATUS.ERROR
        return K8S_DEPLOYMENT_STATUS.PENDING

    def start_k8s_deployment(self, deployment_name):
        _deploy = self.get_deployment_by_name(deployment_name)
        api_instance = client.AppsV1Api(self.api_client)
        if not _deploy:
            raise DeploymentError("Deployment {} not found".format(deployment_name))

        _spec = _deploy.spec
        if _spec.replicas > 0:
            return deployment_name
        _spec.replicas = 1
        api_instance.patch_namespaced_deployment(deployment_name, self.namespace, _deploy)
        LOG.info("Started existed deployment: {}".format(deployment_name))

    def pause_k8s_deployment(self, deployment_name):
        _deploy = self.get_deployment_by_name(deployment_name)
        _spec = _deploy.spec
        _spec.replicas = 0
        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.patch_namespaced_deployment(deployment_name, self.namespace, _deploy)
        except ApiException as e:
            LOG.error("Pause deployment error: {}".format(e))
            raise DeploymentError("Pause {} error {}".format(deployment_name, e))
        LOG.info("Paused existed deployment: {}".format(deployment_name))

    def delete_k8s_deployment(self, deployment_name):
        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_deployment(deployment_name, self.namespace)
        except ApiException as e:
            LOG.error("Delete deployment error: {}".format(e))
            raise DeploymentError("Delete {} error {}".format(deployment_name, e))
        LOG.info("Deleted existed deployment: {}".format(deployment_name))

    ###
    # Service
    ###

    def get_service_by_name(self, service_name, need_raise=True):
        api_instance = client.CoreV1Api(self.api_client)
        try:
            _svc = api_instance.read_namespaced_service(service_name, self.namespace)
        except ApiException:
            if need_raise:
                raise ServiceError("Service {} not found".format(service_name))
            return None
        return _svc.to_dict()

    def create_k8s_service(self, yaml):
        if isinstance(yaml, str) or isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.safe_load(yaml)
        assert isinstance(yaml, dict), "Create a service without legal yaml."

        api_instance = client.CoreV1Api(self.api_client)
        try:
            svc = api_instance.create_namespaced_service(self.namespace, yaml)
            return svc.to_dict()['metadata']['name']
        except ApiException as e:
            LOG.error("Create service error: {}".format(e))
            raise ServiceError("Create service error: {}".format(e))

    def delete_k8s_service(self, service_name):
        api_instance = client.CoreV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_service(service_name, self.namespace)
        except ApiException as e:
            LOG.error("Delete service error: {}".format(e))
            raise ServiceError("Delete service error: {}".format(e))

    ###
    # StatefulSet
    ###

    def create_k8s_statefulset(self, yaml):
        if isinstance(yaml, str) or isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.safe_load(yaml)
        assert isinstance(yaml, dict), "Create a statefulset without legal yaml."

        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.create_namespaced_stateful_set(self.namespace, yaml)
        except ApiException as e:
            LOG.error("Create StatefulSet error: {}".format(e))
            raise StatefulSetError("Create StatefulSet error: {}".format(e))

    def delete_k8s_statefulset(self, statefulset_name):
        api_instance = client.AppsV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_stateful_set(statefulset_name, self.namespace)
        except ApiException as e:
            LOG.error("Delete StatefulSet error: {}".format(e))
            raise StatefulSetError("Delete StatefulSet error: {}".format(e))

    ###
    # PersistentVolumeClaim
    ###

    def create_k8s_pvc(self, yaml):
        if isinstance(yaml, str) or isinstance(yaml, str):
            # Only support ONE deployment yaml
            yaml = yaml_tool.safe_load(yaml)
        assert isinstance(yaml, dict), "Create a PVC without legal yaml."

        api_instance = client.CoreV1Api(self.api_client)
        try:
            api_instance.create_namespaced_persistent_volume_claim(self.namespace, yaml)
        except ApiException as e:
            LOG.error("Create PVC error: {}".format(e))
            raise PVCError("Create PVC error: {}".format(e))

    def delete_k8s_pvc(self, pvc_name):
        api_instance = client.CoreV1Api(self.api_client)
        try:
            api_instance.delete_namespaced_persistent_volume_claim(pvc_name, self.namespace)
        except ApiException as e:
            LOG.error("Delete PVC error: {}".format(e))
            raise PVCError("Delete PVC error: {}".format(e))
