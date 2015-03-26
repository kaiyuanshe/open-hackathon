class ExprStatus:
    Init = 0
    Starting = 1
    Running = 2
    Stopped = 3
    Deleted = 4
    Failed = 5
    Rollbacking = 6
    Rollbacked = 7


class VirtualEnvStatus:
    Init = 0
    Running = 1
    Stopped = 2
    Deleted = 3


class PortBindingType:
    CloudService = 1
    Docker = 2


class VirtualEnvironmentProvider:
    AzureVM = "azure-vm"
    Docker = "docker"


class RemoteProvider:
    Guacamole = "guacamole"


class EmailStatus:
    Primary = 1
    NonPrimary = 0


class ReservedUser:
    DefaultUserID = -1
    DockerVM = -2


class AdminUserHackathonRelStates:
    Actived = 1
    Disabled = 0
