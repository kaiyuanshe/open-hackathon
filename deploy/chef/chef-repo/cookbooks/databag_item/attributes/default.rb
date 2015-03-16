default[:databag_item] = {
	:secret_source => "none", # none, local, S3, or http
	:path => nil,
	:username => nil,
	:password => nil,
	:bucket => nil			  # only used if secret_source=S3
}
