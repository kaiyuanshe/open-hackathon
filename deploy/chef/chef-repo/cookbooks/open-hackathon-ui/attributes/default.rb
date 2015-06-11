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


# container attributes
default['openhackathon'][:ui][:src_dir] = "#{openhackathon[:base_dir]}/open-hackathon-ui"
default['openhackathon'][:ui][:debug] = true
default['openhackathon'][:ui][:config_file] = "#{openhackathon[:ui][:src_dir]}/config.json"

default['openhackathon'][:ui][:hostname] = 'open-hackathon-dev.chinacloudapp.cn'
default['openhackathon'][:ui][:hackathon_name] = 'kaiyuanshe'
default['openhackathon'][:ui][:login_provider] ='["github", "qq", "weibo", "gitcafe","live"]'

# forever param
default['openhackathon'][:ui][:forever][:spin_sleep_time] = 2000
default['openhackathon'][:ui][:forever][:min_uptime] = 5000

# log
default['openhackathon'][:ui][:log][:log_file] = "#{openhackathon[:log_dir]}/open-hackathon-ui.log"
default['openhackathon'][:ui][:log][:rotate_frequency] = "daily"
default['openhackathon'][:ui][:log][:rotate] = 30
