tomcat Cookbook
===============
This is a simple rehashing of the tomcat cookbook taking out a lot of the complicated things that don't work and aren't needed
to make a simple deploy and a simple configuration with some new configuration options via libraries and valves.

Requirements
------------
Yum Based Linux (RHEL, Centos, Fedora, Amazon)

#### Packages
OpenJDK-1.7.0
Tomcat7

Attributes
----------

#### tomcat::default
<table>
  <tr>
    <th>Key</th>
    <th>Type</th>
    <th>Description</th>
    <th>Default</th>
  </tr>
  <tr>
    <td><tt>['tomcat']['port']</tt></td>
    <td>Int</td>
    <td>What port for tomcat to listen on</td>
    <td><tt>8080</tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['proxy_port']</tt></td>
    <td>Int</td>
    <td>Tomcat Proxy Port</td>
    <td><tt>nil</tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['max_threads']</tt></td>
    <td>Int</td>
    <td>Tomcat's Max Threads</td>
    <td><tt>nil</tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['ssl_proxy_port']</tt></td>
    <td>Int</td>
    <td>Tomcat's SSL Proxy Port</td>
    <td><tt>nil</tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['catalina_options']</tt></td>
    <td>String</td>
    <td>Tomcat's Catalina Options</td>
    <td><tt></tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['java_options']</tt></td>
    <td>String</td>
    <td>Options to the JVM</td>
    <td><tt>-Xmx128M -Djava.awt.headless=true</tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['nexus']</tt></td>
    <td>String</td>
    <td>URL of Nexus Server</td>
    <td><tt></tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['extras']['jmx']</tt></td>
    <td>Boolean</td>
    <td>Add the JMX Jar to the tomcat bin</td>
    <td><tt>True</tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['extras']['web']</tt></td>
    <td>Boolean</td>
    <td>Add the Web Services Jar to the tomcat bin</td>
    <td><tt>True</tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['extras']['juli']</tt></td>
    <td>Boolean</td>
    <td>Add the Tomcat Juli to the tomcat bin</td>
    <td><tt>True</tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['extras']['log4j']</tt></td>
    <td>Boolean</td>
    <td>Add the Juli adapter for log4j to the tomcat bin</td>
    <td><tt>True</tt></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['valves']</tt></td>
    <td>List</td>
    <td>A list of Hashes describing valves to put into the server.xml</td>
    <td></td>
  </tr>
  <tr>
    <td><tt>['tomcat']['libs']</tt></td>
    <td>List</td>
    <td>A list of Hashes describing artifacts to retreive from Nexus for the Tomcat lib directory</td>
    <td></td>
  </tr>
</table>

Usage
-----
#### tomcat::default

e.g.
Just include `tomcat` in your node's `run_list`:

:


```json
{
  "name":"my_node",
  "run_list": [
    "recipe[tomcat]"
  ]
}
```

Contributing
------------
TODO: (optional) If this is a public cookbook, detail the process for contributing. If this is a private cookbook, remove this section.

e.g.
1. Fork the repository on Github
2. Create a named feature branch (like `add_component_x`)
3. Write your change
4. Write tests for your change (if applicable)
5. Run the tests, ensuring they all pass
6. Submit a Pull Request using Github

License and Authors
-------------------
Authors: Stephen Carman (scarman@coldlight.com)
