default['tomcat']['port'] 		= 8080
default['tomcat']['proxy_port'] 	= nil
default['tomcat']['max_threads'] 	= nil
default['tomcat']['ssl_proxy_port'] 	= nil
default['tomcat']['shutdown_port'] 	= 8005
default['tomcat']['catalina_options'] 	= ''
default['tomcat']['java_options'] 	= '-Xmx128M -Djava.awt.headless=true'
default['tomcat']['nexus'] 		= ''
default['tomcat']['extras']['jmx']	= false
default['tomcat']['extras']['web']	= false
default['tomcat']['extras']['juli']	= true
default['tomcat']['extras']['log4j']	= true
default['tomcat']['extras']['jmx_url']	= 'http://apache.osuosl.org/tomcat/tomcat-7/v7.0.57/bin/extras/catalina-jmx-remote.jar'
default['tomcat']['extras']['web_url']	= 'http://apache.osuosl.org/tomcat/tomcat-7/v7.0.57/bin/extras/catalina-ws.jar'
default['tomcat']['extras']['juli_url']	= 'http://apache.osuosl.org/tomcat/tomcat-7/v7.0.57/bin/extras/tomcat-juli-adapters.jar'
default['tomcat']['extras']['log4j_url']= 'http://apache.osuosl.org/tomcat/tomcat-7/v7.0.57/bin/extras/tomcat-juli.jar'
default['tomcat']['valves'] = [
				{
				  "className"	 => 'org.apache.catalina.valves.AccessLogValve',
				  "directory"	 => 'logs',
				  "prefix" 	 => 'local_host_access_log.',
				  "suffix"	 => '.txt',
				  "pattern"	 => 'common',
				  "resolveHosts" => 'false'
				}
			]
default['tomcat']['libs'] = [
				{
				  "groupId" 	=> 'ch.qos.logback',
				  "artifactId" 	=> 'logback-access',
				  "version" 	=> '1.1.2',
				  "packaging" 	=> 'jar',
				  "repository" 	=> 'public'
				},
				{
                                  "groupId" 	=> 'ch.qos.logback',
                                  "artifactId" 	=> 'logback-core',
                                  "version" 	=> '1.1.2',
                                  "packaging" 	=> 'jar',
                                  "repository" 	=> 'public'
				},
				{
                                  "groupId" 	=> 'net.logstash.logback',
                                  "artifactId" 	=> 'logstash-logback-encoder',
                                  "version" 	=> '3.7-SNAPSHOT',
                                  "packaging" 	=> 'jar',
                                  "repository" 	=> 'public'
				}
			]

case node['platform']
when 'centos', 'fedora'
	default['tomcat']['package'] 		= 'tomcat'
	default['tomcat']['service'] 		= 'tomcat'	
	default['tomcat']['user'] 		= 'tomcat'
	default['tomcat']['group'] 		= 'tomcat'
	default['tomcat']['home'] 		= "/usr/share/tomcat"
	default['tomcat']['base'] 		= "/usr/share/tomcat"
	default['tomcat']['config_dir'] 	= "/etc/tomcat"
	default['tomcat']['log_dir'] 		= "/var/log/tomcat"
	default['tomcat']['tmp_dir'] 		= "/var/cache/tomcat/temp"
	default['tomcat']['work_dir'] 		= "/var/cache/tomcat/work"
	default['tomcat']['context_dir'] 	= "#{node['tomcat']['config_dir']}/Catalina/localhost"
	default['tomcat']['webapp_dir'] 	= "#{node['tomcat']['home']}/webapps"
	default['tomcat']['lib_dir'] 		= "#{node['tomcat']['home']}/lib"
	default['tomcat']['bin_dir']		= "#{node['tomcat']['home']}/bin"
	default['tomcat']['endorsed_dir'] 	= "#{node['tomcat']['lib_dir']}/endorsed"
when 'redhat',  'amazon'
	default['tomcat']['package'] 		= 'tomcat7'
	default['tomcat']['service'] 		= 'tomcat7'
	default['tomcat']['user'] 		= 'tomcat'
	default['tomcat']['group'] 		= 'tomcat'
	default['tomcat']['home'] 		= "/usr/share/tomcat7"
	default['tomcat']['base'] 		= "/usr/share/tomcat7"
	default['tomcat']['config_dir'] 	= "/etc/tomcat7"
	default['tomcat']['log_dir'] 		= "/var/log/tomcat7"
	default['tomcat']['tmp_dir'] 		= "/var/cache/tomcat7/temp"
	default['tomcat']['work_dir'] 		= "/var/cache/tomcat7/work"
	default['tomcat']['context_dir'] 	= "#{node['tomcat']['config_dir']}/Catalina/localhost"
	default['tomcat']['webapp_dir'] 	= "#{node['tomcat']['home']}/webapps"
	default['tomcat']['lib_dir'] 		= "#{node['tomcat']['home']}/lib"
	default['tomcat']['endorsed_dir'] 	= "#{node['tomcat']['lib_dir']}/endorsed"
end
