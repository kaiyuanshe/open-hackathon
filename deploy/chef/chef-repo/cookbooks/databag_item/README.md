Description
===========
A cookbook that helps to manage and load attributes from databag. The cookbook did the following tasks
* Provide a common interface to access encrypted and plain databags
* Provide a common interface for Chef server and Chef Solo
* Load secrets from difference sources, including local file, S3 bucket, or HTTP source (for example, user data)
* Automatically fallback to environment if the attributes doesn't exist in data bag. This is for backward compatibility.

Requirements
============
Tested in Chef 11.8.0

Attributes
==========
* `node['databag_item']['secret_source']` - specified where the secret should be loaded. The value can be one of the following:
  * `none` - There is no secret file. The data bag is in plain text
  * `S3` - Load the secret file from S3 bucket
  * `file` - Load the secret file from local file system
  * `HTTP` - Load the secret from HTTP source. This can be useful when the secret is put in the EC2 user data for example.
* `node['databag_item']['path']` - path of the secret file

S3 settings
----------------

* `node['databag_item']['bucket']` - the S3 bucket name. 
* `node['databag_item']['username']` - the AWS key. If it is not specified, the cookbook will figure it out from IAM role.
* `node['databag_item']['password']` - the AWS secret. If it is not specified, the cookbook will figure it out from IAM role.

Usage
=====

The cookbook assumes that your data_bag folder is organized like following:
```
data_bags
├── abus-dev
│   ├── default.json
│   └── my-bag.json
├── abus-vmware
│   └── default.json
└── README.md
```
* Each data bag use environment as its name. The `databag_item` cookbook will automatically load proper databag by environment name.
* There is a default.json item in each databag, which will be loaded when no data item is specified. (see example below)


# Access databag attributes
1. Add depedency to your cookbook's `metadata.rb`
```ruby
depends	"databag_item"
```

2. Access to attributes in databag. By convension, the databag is organized by environment name. The following sample would access to attributes to the `default` bag by default:
```ruby
databag_item[:attribute]
```
The attributes can be accessed from recipies, resources, or templates

You could also directly access to the attribute as if it is part of the environment:
```ruby
node[:attribute]
```
This can be very useful if you are using community cookbook and want to put some attributes in databag.

3. If needs to access to bag other than `secrets`,  the code could be like following:
```ruby
databag_item('my-bag')[:attribute]
```
