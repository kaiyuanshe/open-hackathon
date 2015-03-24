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
    HACKATHON_ID = "hackathon_id"


class OAUTH_PROVIDER:
    GITHUB = "github"
    QQ = "qq"
    GITCAFE = "gitcafe"
    WEIBO = "weibo"


class HEALTH_STATE:
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


class ADMIN:
    SUPER_ADMIN_GROUP_ID = 1
    DEFAULT_SUPER_ADMIN_EMAIL = "2303202961@qq.com"