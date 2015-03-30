open-hackathon-ui Cookbook
==================
This cookbook makes open-hackathon-ui.

Requirements
------------

#### packages
- `apt` - Hackathon-ui needs "apt" cookbook.
- `git` - "git" cookbook.
- `python` - "python" cookbook.
- `uwsgi` - "uwsgi" cookbook.

Attributes
----------

#### open-hackathon-ui::default
<table>
  <tr>
    <th>Key</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default</th>
  </tr>
  <tr>
    <td><tt>['open-hackathon-ui']['HOSTNAME']</tt></td>
    <td>string</td>
    <td>hostname</td>
    <td><tt>'http://open-hackathon-dev.chinacloudapp.cn'</tt></td>
  </tr>
  <tr>
    <td><tt>['open-hackathon-ui']['HACKATHON_API_ENDPOINT']</tt></td>
    <td>string</td>
    <td>hackathon api endpoint</td>
    <td><tt>'http://open-hackathon.chinacloudapp.cn:15002'</tt></td>
  </tr>
  <tr>
    <td><tt>['open-hackathon-ui']['provider']</tt></td>
    <td>string</td>
    <td>the platform that we support</td>
    <td><tt>'["github","qq","gitcafe","weibo"]'</tt></td>
  </tr>

</table>

Usage
-----
#### open-hackathon-ui::default

Just include `open-hackathon-ui` in your node's `run_list`:

```json
{
  "name":"my_node",
  "run_list": [
    "recipe[open-hackathon-ui]"
  ]
}
```

License and Authors
-------------------
Authors: msopentechcn
