# -*- coding: utf-8 -*-
"""
Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
 
The MIT License (MIT)
 
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__all__ = ["factory", "RequiredFeature"]


#
# Hackathon factory
# call 'factory.provide' to fill object into factory
# instantiate 'RequiredFeature' to get certain object from factory
#
class HackathonFactory:
    def __init__(self, allow_replace=False):
        """Create a new factory

        :param allow_replace: whether to replace existing provider with same feature. AssertionException will be raised it's
        False and more than one providers with same key(feature) are provided
        """
        self.providers = {}
        self.allow_replace = allow_replace

    def set_allow_replace(self, allow_replace):
        """Set the value of allow_replace"""
        self.allow_replace = allow_replace

    def provide(self, feature, provider, suspend_callable=False, *args, **kwargs):
        """Add a provider to factory

        :type feature: str|unicode
        :param feature: key to store and get the object into/from the factory

        :type provider: object | callable
        :param provider: the object to be added.

        :type suspend_callable: boolean
        :param suspend_callable: suspend the callable where we want to keep the original function

        :Example:
            from *** import UserManager
            factory.provide("user_manager", UesrManager)
            factory.provide("user_manager", UesrManager, *init_args, **init_kwargs)

            # or:
            um = UserManager
            factory.provide("user_manager", um)

        """
        if not self.allow_replace:
            assert not self.providers.has_key(feature), "Duplicate feature: %r" % feature
        if callable(provider) and not suspend_callable:
            def call():
                return provider(*args, **kwargs)
        else:
            def call():
                return provider
        self.providers[feature] = call

    def __getitem__(self, feature):
        try:
            provider = self.providers[feature]
        except KeyError:
            raise KeyError, "Unknown feature named %r" % feature
        return provider()


factory = HackathonFactory()


#
# Some basic assertions to test the suitability of injected features
#

def NoAssertion(obj):
    return True


def IsInstanceOf(*classes):
    def test(obj):
        return isinstance(obj, classes)

    return test


def HasAttributes(*attributes):
    def test(obj):
        for each in attributes:
            if not hasattr(obj, each): return False
        return True

    return test


def HasMethods(*methods):
    def test(obj):
        for each in methods:
            try:
                attr = getattr(obj, each)
            except AttributeError:
                return False
            if not callable(attr): return False
        return True

    return test


#
# An attribute descriptor to "declare" required features
#

class RequiredFeature(object):
    def __init__(self, feature, assertion=NoAssertion):
        """Create instance of RequiredFeature.

        Will get the actual target from factory upon the first call.

        :type feature: str|unicode
        :param feature: the key to get object from factory

        :Example:
            inst = RequiredFeature("user_manager")
            inst.some_method() # where user_manager.some_method will be called

        :raise:
            KeyError if feature doesn't exist in factory.
        """
        self.feature = feature
        self.assertion = assertion

    def __get__(self, obj, T):
        return self.result  # <-- will request the feature upon first call

    def __getattr__(self, name):
        self.result = self.request()
        if name == "result":
            return self.result
        else:
            return getattr(self.result, name)

    def request(self):
        obj = factory[self.feature]
        assert self.assertion(obj), \
            "The value %r of %r does not match the specified criteria" \
            % (obj, self.feature)
        return obj
