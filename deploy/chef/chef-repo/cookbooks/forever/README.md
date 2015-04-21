# chef-forever

[Chef](http://www.opscode.com/chef/) cookbook for running node apps using [forever](https://github.com/nodejitsu/forever/).

## Installation

Easiest way to install this cookbook is to use [librarian-chef](https://github.com/applicationsonline/librarian#librarian-chef).

Add this to your Cheffile:

```ruby

cookbook 'forever',
  :git => 'https://github.com/trabian/chef-forever'

```

There are of course many other ways.

## Usage

```ruby

include_recipe "forever"

forever_service "statsd" do
  user 'statsd'
  group 'statsd'
  path "/web/statsd"
  script "stats.js"
  script_options "myConfig.js"
  description "Simple daemon for easy stats aggregation."
  action [ :enable, :start ]
end

```

## License and Author

License: [MIT](https://github.com/trabian/chef-forever/blob/master/LICENSE)

Author: [David Radcliffe](https://github.com/dwradcliffe)

