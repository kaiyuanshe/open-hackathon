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

case node['platform_family']
when 'windows'
  default['git']['version'] = "1.8.0-preview20121022"
  default['git']['url'] = "http://github.com/downloads/msysgit/git/Git-#{node['git']['version']}.exe"
  default['git']['checksum'] = "8ec19d04912fd27d7350823c857a4807b550fa63a3744bf6fd2841de8cfa9a0f"
  default['git']['display_name'] = "Git version #{ node['git']['version'] }"
when "mac_os_x"
  default['git']['osx_dmg']['app_name']    = "git-1.8.0-intel-universal-snow-leopard"
  default['git']['osx_dmg']['volumes_dir'] = "Git 1.8.0 Snow Leopard Intel Universal"
  default['git']['osx_dmg']['package_id']  = "GitOSX.Installer.git180.git.pkg"
  default['git']['osx_dmg']['url']         = "https://github.com/downloads/timcharper/git_osx_installer/git-1.8.0-intel-universal-snow-leopard.dmg"
  default['git']['osx_dmg']['checksum']    = "da83499f3305061792358bec26c20faa997b7ad9990713d1be2b03cbb5fbce12"
else
  default['git']['prefix'] = "/usr/local"
  default['git']['version'] = "1.8.0"
  default['git']['url'] = "https://github.com/git/git/tarball/v#{node['git']['version']}"
  default['git']['checksum'] = "24f1895fa74a23b3d9233fa89a9ef04d83a1cd952d659720d6ea231bbd0c973c"
end
