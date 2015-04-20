open-hackathon-api Cookbook
=================
This cookbook is about how to auto-deploy open-hackathon backend of api with chef.

Requirements
----------
#### packages
- `apt` - apt.
- `python` - python.
- `uwsgi` - uwsgi.
- `git` - git.
- `mysql` - ~>6.0.20
- `postgresql` - postgresql.
- `database` - database.
- `mysql2_chef_gem` - mysql2-chef-gem

Attributes
----------

#### back-end::default
<table>
  <tr>
    <th>Key</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default</th>
  </tr>
  <tr>
    <td><tt>['open-hackathon-api']['guacamole']['host']</tt></td>
    <td>string</td>
    <td>the host of guacamole server</td>
    <td><tt>http://localhost:8080</tt></td>
  </tr>
</table>

Usage
-----
#### back-end::default
Just include `open-hackathon-api` in your node's `run_list`:

```json
{
  "name":"my_node",
  "run_list": [
    "recipe[open-hackathon-api]"
  ]
}
```

Contributing
------------

License and Authors
-------------------

