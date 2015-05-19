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


class DockerTemplateUnit(object):
    T_N = 'name'
    T_I = 'image'
    T_P = 'ports'
    T_P_N = 'name'
    T_P_PO = 'port'
    T_P_PU = 'public'
    T_AI = 'AttachStdin'
    T_AO = 'AttachStdout'
    T_AE = 'AttachStderr'
    T_T = 'tty'
    T_SO = 'stdin_open'
    T_R = 'remote'
    T_R_PV = 'provider'
    T_R_PT = 'protocol'
    T_R_U = 'username'
    T_R_PA = 'password'
    T_R_PO = 'port'

    def __init__(self, dic):
        self.dic = self.load_default_config()
        for key, value in dic.iteritems():
            self.dic[key] = value

    def load_default_config(self):
        dic = {
            self.T_N: 'ubuntu',
            self.T_I: 'sffamily/ubuntu-gnome-vnc-eclipse',
            self.T_P: [
                {
                    self.T_P_N: 'website',
                    self.T_P_PO: 80,
                    self.T_P_PU: True,
                },
                {
                    self.T_P_N: 'vnc',
                    self.T_P_PO: 5901,
                    self.T_P_PU: True,
                },
            ],
            self.T_AI: False,
            self.T_AO: True,
            self.T_AE: True,
            self.T_T: True,
            self.T_SO: True,
            self.T_R: {
                self.T_R_PV: 'guacamole',
                self.T_R_PT: 'vnc',
                self.T_R_U: 'root',
                self.T_R_PA: 'acoman',
                self.T_R_PO: 5901,
            },
        }
        return dic