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

import sys

sys.path.append("..")

import abc

from hackathon import Component

__all__ = ["ExprStarter"]


class ExprStarter(Component):
    """Base for experiment starter"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def start_expr(self, context):
        """To start a new Experiment asynchronously

        :type context: Context
        :param context: the execution context.

        """
        pass

    @abc.abstractmethod
    def stop_expr(self, context):
        """Stop experiment asynchronously

        :type context: Context
        :param context: the execution context.

        """
        pass

    @abc.abstractmethod
    def rollback(self, context):
        """cancel/rollback a expr which is in error state

        :type context: Context
        :param context: the execution context.

        """
        pass
