{
    "expr_name": "docker-template-sample",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "ubuntu",
            "Hostname": "",
            "Domainname": "",
            "User": "",
            "AttachStdin": false,
            "AttachStdout": true,
            "AttachStderr": true,
            "Tty": true,
            "OpenStdin": true,
            "StdinOnce": false,
            "Env": ["JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/jre/"],
            "Cmd": ["/usr/sbin/sshd", "-D"],
            "Entrypoint": null,
            "Image": "sffamily/ampcamp5:v4",
            "Labels": {},
            "Volumes": null,
            "WorkingDir": "",
            "NetworkDisabled": false,
            "MacAddress": "",
            "ExposedPorts":[{
                "name": "Tachyon",
                "port": 19999,
                "public": true,
                "protocol": "tcp",
                "url": "http://{0}:{1}"
            },{
                "name": "Deploy",
                "port": 22,
                "public": true,
                "protocol": "tcp"
            },{
                "name": "WebUI",
                "port": 4040,
                "public": true,
                "protocol": "tcp",
                "url": "http://{0}:{1}"
            }],
            "remote": {
                "provider": "guacamole",
                "protocol": "vnc",
                "username": "root",
                "password": "acoman",
                "port": 5901
            },
            "SecurityOpts": [""],
            "HostConfig": {
                "Binds": null,
                "Links": null,
                "LxcConf": null,
                "Memory": 0,
                "MemorySwap": 0,
                "CpuShares": 0,
                "CpusetCpus": "",
                "PublishAllPorts": false,
                "Privileged": false,
                "ReadonlyRootfs": false,
                "Dns": null,
                "DnsSearch": null,
                "ExtraHosts": null,
                "VolumesFrom": null,
                "CapAdd": null,
                "CapDrop": null,
                "RestartPolicy": { "Name": "", "MaximumRetryCount": 0 },
                "NetworkMode": "",
                "Devices": null,
                "Ulimits": null,
                "LogConfig": { "Type": "json-file", Config: {} },
                "CgroupParent": ""
            }
        }
    ]
}