name             "databag_item"
maintainer       "Microsoft Open Technologies (Shanghai) Co. Ltd"
maintainer_email "msopentechdevsh@microsoft.com"
license          "MIT"
description      "Load items from databag, without worry about secrets"
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          "1.1.1"

%w{ citadel }.each do |cb|
  depends cb
end