# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
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

default['open-hackathon']['admin']['HOSTNAME'] = 'http://hack-admin-dev.chinacloudapp.cn'
default['open-hackathon']['HACKATHON_API_ENDPOINT'] = 'http://open-hackathon.chinacloudapp.cn:15002'

default['open-hackathon']['hackathon']['name'] = 'open-xml-sdk'

default['open-hackathon']['admin']['login_provider'] ='["github","qq"]'
default['open-hackathon']['admin']['session_minutes'] = '60'
default['open-hackathon']['admin']['token_expiration_minutes'] = '60*24'

default['open-hackathon']['admin']['app']['secret_key'] = 'secret_key'
default['open-hackathon']['admin']['src_dir'] = '#{open-hackathon[:base_dir]}/open-hackathon-adminUI/src'
default['open-hackathon']['admin']['port'] = 80
