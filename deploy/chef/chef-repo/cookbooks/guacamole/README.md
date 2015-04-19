# guacamole cookbook

Install and configure [guacamole](http://guac-dev.org/), an HTML5
clientless remote desktop tunnel/proxy server.

This cookbook is currently ***EXPERIMENTAL***, And is currently
only tested by the author.

**Testing on other platforms and pull requests are definitely welcome!**

# Requirements

Platform:

* Debian, Ubuntu

The following cookbooks are dependencies:

* apt

* tomcat

# Usage

# Attributes

# Recipes

* default -- Installs guacamole using distro packages.

* sourceforge -- Downloads guacamole packages from sourceforge tarball
  and creates a local package repository to install from.

# Author

Author:: Jeff Dutton (<jeff.dutton@stratus.com>)

Copyright:: 2012, Jeff Dutton

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
