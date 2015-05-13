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

from hackathon.log import (
    log,
)
from os.path import (
    realpath,
    dirname,
    abspath,
)
import json
import os


class BaseTemplate(object):
    """
    Base class of template
    """
    T_EN = 'expr_name'
    T_VE = 'virtual_environments'
    T_VE_P = 'provider'

    def __init__(self, expr_name):
        self.dic = {
            self.T_EN: expr_name,
        }

    def to_file(self):
        """
        Dump to disk as json file, an existing file with the same name will be erased
        :return: absolute path of json file
        """
        template_dir = '%s/../resources' % dirname(realpath(__file__))
        # check template dir whether exists
        if not os.path.isdir(template_dir):
            log.debug('template dir [%s] not exists' % template_dir)
            os.mkdir(template_dir)
        template_path = '%s/%s.js' % (template_dir, self.dic[self.T_EN])
        with open(template_path, 'w') as template_file:
            json.dump(self.dic, template_file)
        return abspath(template_path)