name             "databag_item"
maintainer       "Autodesk"
maintainer_email "tingjie.zhu@autodesk.com"
license          "Apache 2.0"
description      "Load items from databag, without worry about secrets"
long_description IO.read(File.join(File.dirname(__FILE__), 'README.md'))
version          "1.1.0"

%w{ citadel }.each do |cb|
  depends cb
end