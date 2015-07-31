__author__ = 'root'

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

from hackathon import Component


__all__ = ["CacheManager"]


class CacheManagerExt(Component):
    """To cache resource"""
    def get_cache(self, **kwargs):
        """get cached data

        :param kwargs: include two pairs of key-values: key=key_name, createfunc=func(a,b)

        :return: the value mapped to the key

        :example:
            CacheManager.get_cache(key="abc", createfunc=func(a,b))

        """
        results = self.tmpl_cache.get(**kwargs)
        return results

    def invalidate(self, key):
        """remove the key-value pair in the cache

        :param key: the key_name

        :rtype bool
        :return: if remove the key-value pair correctly

        """
        try:
            self.tmpl_cache.remove_value(key=key)
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def clear(self):
        """clear all the cache

        :rtype bool
        :return: if clear the cache correctly
        """
        try:
            self.tmpl_cache.clear()
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def __init__(self):
        """initialize the class CacheManager

        """
        self.cache_opts = {
            'cache.type': 'file',
            # can be "memory" or "file"
            'cache.data_dir': '/tmp/cache/data',
            'cache.lock_dir': '/tmp/cache/lock'
        }
        self.cache = CacheManager(**parse_cache_config_options(self.cache_opts))
        self.tmpl_cache = self.cache.get_cache('mytemplate', type='file', expire=3600)
