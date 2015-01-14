class ExprStatus:
    Init = 0
    Starting = 1
    Running = 2
    Stopped = 3
    Deleted = 4
    Failed = 5
    Rollbacking = 6
    Rollbacked = 7


class ContainerStatus:
    Init = 0
    Running = 1
    Stopped = 2
    Deleted = 3