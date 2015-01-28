# guacamole container constants
class GUACAMOLE:
    STATUS = "guacamole_status"
    IMAGE = "hall/guacamole"
    PORT = 8080


# DEFAULT ROLES
class ROLE:
    ADMIN = "admin"
    HOST = "host"


# docker
class DOCKER:
    DEFAULT_REMOTE_PORT = 4243


class HTTP_HEADER:
    TOKEN = "token"


class OAUTH_PROVIDER:
    GITHUB = "github"
    QQ = "qq"


class HEALTH_STATE:
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"