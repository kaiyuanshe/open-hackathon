# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------------
# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#  
# The MIT License (MIT)
#  
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#  
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#  
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------------

import sys

sys.path.append("../src/hackathon")
from mock import Mock
import unittest
from hackathon.docker import OssDocker
from hackathon.database import db_adapter
from hackathon.database.models import DockerHostServer


class TestDocker(unittest.TestCase):
    @unittest.skip("not ready")
    def test_host_ports(self):
        mock_cache = Mock()
        mock_cache.host_ports = []
        for i in range(0, 29):
            OssDocker.host_ports.append(i)
            mock_cache.host_ports.append(i)
        mock_cache.host_ports.append(10001)
        docker1 = OssDocker()
        return_port = docker1.get_available_host_port(db_adapter.find_first_object_by(DockerHostServer, id=1), 1)
        self.assertEqual(10001, return_port)
        self.assertListEqual(mock_cache.host_ports, OssDocker.host_ports)

        docker2 = OssDocker()
        mock_cache.host_ports = [10002]
        return_port = docker2.get_available_host_port(db_adapter.find_first_object_by(DockerHostServer, id=1), 2)
        self.assertEqual(10002, return_port)
        self.assertListEqual(mock_cache.host_ports, OssDocker.host_ports)