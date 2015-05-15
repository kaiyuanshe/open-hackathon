guacamole Cookbook
==================

This cookbook makes guacamole.

Requirements
------------

#### packages
- `java` - guacamole needs java.
- `tomcat` - guacamole needs tomcat.
- `open-hackathon-api` - guacamole needs open-hackathon-api.

Attributes
----------

#### guacamole::default
<table>
  <tr>
    <th>Key</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default</th>
  </tr>
  <tr>
    <td><tt>['guacamole']['lib-directory']</tt></td>
    <td>String</td>
    <td>where to put related properties & json files</td>
    <td><tt>/etc/guacamole</tt></td>
  </tr>
</table>

Usage
-----
#### guacamole::default

Just include `guacamole` in your node's `run_list`:

```json
{
  "name":"my_node",
  "run_list": [
    "recipe[guacamole]"
  ]
}
```

Contributing
------------


License and Authors
-------------------
 Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
  
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
