{
    "expr_name": "docker-template-sample",
    "virtual_environments":
    [
        {
            "provider": "docker",
            "name": "web",
            "ports":
            [
                {
                    "name": "Tachyon",
                    "port": 19999,
                    "public": true,
                    "protocol": "tcp",
                    "url": "http://{0}:{1}"
                },
                {
                    "name": "Deploy",
                    "port": 22,
                    "public": true,
                    "protocol": "tcp"
                },
                {
                    "name": "WebUI",
                    "port": 4040,
                    "public": true,
                    "protocol": "tcp",
                    "url": "http://{0}:{1}"
                }
            ],
            "remote":
            {
                "provider": "guacamole",
                "protocol": "ssh",
                "username": "root",
                "password": "root",
                "port": 22
            },
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
            "Entrypoint": "",
            "Image": "sffamily/ampcamp5:v5",
            "Labels": {},
            "Volumes": {},
            "WorkingDir": "",
            "NetworkDisabled": false,
            "MacAddress": "",
            "SecurityOpts": [""],
            "HostConfig":
            {
                "Binds": [],
                "Links": [],
                "LxcConf": {},
                "Memory": 0,
                "MemorySwap": 0,
                "CpuShares": 0,
                "CpusetCpus": "",
                "PortBindings": {},
                "PublishAllPorts": false,
                "Privileged": false,
                "ReadonlyRootfs": false,
                "Dns": [],
                "DnsSearch": [],
                "ExtraHosts": [],
                "VolumesFrom": [],
                "CapAdd": [],
                "CapDrop": [],
                "RestartPolicy": { "Name": "", "MaximumRetryCount": 0 },
                "NetworkMode": "",
                "Devices": [],
                "Ulimits": [],
                "LogConfig": { "Type": "json-file", "Config": {} },
                "CgroupParent": ""
            }
        }
    ]
}