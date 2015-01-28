__author__ = 'Yifu Huang'

from abc import *


class CloudABC:
    """
    Abstract base class for cloud service management
    Any specific cloud service management should inherit from this class
    Currently support only Azure
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def connect(self, user_info):
        """
        Connect to cloud according to given user_info
        :param user_info:
        :return:
        """
        pass

    @abstractmethod
    def create_async(self, user_template):
        """
        Create virtual machines according to give user template
        :param user_template:
        :return:
        """
        pass

    @abstractmethod
    def update_async(self, user_template, update_template):
        """
        Update virtual machines created by user template according to given update template
        :param user_template:
        :return:
        """
        pass

    @abstractmethod
    def delete_async(self, user_template):
        """
        Delete virtual machines according to given user template
        :param user_template:
        :return:
        """
        pass

    @abstractmethod
    def shutdown_async(self, user_template):
        """
        Shutdown virtual machines according to given user template
        :param user_template:
        :return:
        """
        pass

    @abstractmethod
    def create_sync(self, user_template):
        """
        Create virtual machines according to give user template
        :param user_template:
        :return:
        """
        pass

    @abstractmethod
    def update_sync(self, user_template, update_template):
        """
        Update virtual machines created by user template according to given update template
        :param user_template:
        :return:
        """
        pass

    @abstractmethod
    def delete_sync(self, user_template):
        """
        Delete virtual machines according to given user template
        :param user_template:
        :return:
        """
        pass

    @abstractmethod
    def shutdown_sync(self, user_template):
        """
        Shutdown virtual machines according to given user template
        :param user_template:
        :return:
        """
        pass