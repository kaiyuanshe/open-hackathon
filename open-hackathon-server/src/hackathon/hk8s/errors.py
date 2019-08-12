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
