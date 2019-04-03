class BaseError(Exception):
    err_id = ""
    err_msg_format = "{}: {}"

    def __init__(self, err_msg):
        self._err_msg = err_msg

    @property
    def err_msg(self):
        return self.err_msg_format.format(self.err_id, self._err_msg)


class YmlParseError(BaseError):
    err_id = "K8s Yaml parse error"


class EnvError(BaseError):
    err_id = "K8s environment error"


class DeploymentError(EnvError):
    err_id = "K8s deployment error"


class ServiceError(EnvError):
    err_id = "K8s service error"

