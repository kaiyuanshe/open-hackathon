# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

from hackathon import Component


__all__ = ["CacheManagerExt"]


class CacheManagerExt(Component):
    """To cache resource"""
    def get_cache(self, key, createfunc):
        """Get cached data of the returns of createfunc depending on the key.
        If key and createfunc exist in cache, returns the cached data,
        otherwise caches the returns of createfunc and returns data.

        :type key: String
        :param key: key name, present the unique key each time caching

        :type createfunc: function object
        :param createfunc: only the name of function, have no parameters,
            its return type can be any basic object, like String, int, tuple, list, dict, etc.

        :rtype: String
        :return: the value mapped to the key

        :example:
            CacheManager.get_cache(key="abc", createfunc=func)

        """
        results = self.tmpl_cache.get(key=key, createfunc=createfunc)
        return results

    def invalidate(self, key):
        """remove the key-value pair in the cache

        :type key: String
        :param key: key name, present the unique key each time caching

        :rtype: bool
        :return: True if remove the key-value pair correctly, otherwise False

        """
        try:
            self.tmpl_cache.remove_value(key=key)
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def clear(self):
        """clear all the cache

        :rtype: bool
        :return: True if clear the cache correctly, otherwise False
        """
        try:
            self.tmpl_cache.clear()
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def __init__(self):
        """initialize the class CacheManager
        More configuration refer to http://beaker.readthedocs.org/en/latest/caching.html#about
        """
        # store the basic configuration
        self.cache_opts = {
            'cache.type': 'memory',
            # can be "memory" or "file"
            'cache.data_dir': '/tmp/cache/data',
            'cache.lock_dir': '/tmp/cache/lock'
        }
        # create CacheManager instance with cache_opts
        self.cache = CacheManager(**parse_cache_config_options(self.cache_opts))
        # In addition to the defaults supplied to the CacheManager instance,
        # any of the Cache options can be changed on a per-namespace basis,
        # by setting a type, and expire option.
        self.tmpl_cache = self.cache.get_cache('mytemplate', type='file', expire=3600)
