{
    "name": "sample-template-for-docker",
    "description": "ampcamp 2015",
    "provider": "docker",
    "virtual_environments":
    [
        {
            "provider": 0,
            "name": "web",
            "type": "ubuntu terminal",
            "description": "sample environment for ampcamp 2015",
            "ports":
            [
                {
                    "name": "website",
                    "port": 80,
                    "public": true,
                    "protocol": "tcp",
                    "url": "http://{0}:{1}"
                },
                {
                    "name": "ssh",
                    "port": 22,
                    "public": true,
                    "protocol": "tcp"
                },
                {
                    "name": "mysql",
                    "port": 3306,
                    "public": false,
                    "protocol": "tcp"
                }
            ],
            "remote":
            {
                "provider": "guacamole",
                "protocol": "ssh",
                "username": "root",
                "password": "acowoman",
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
            "Env": ["ROOT_PASS=acowoman"],
            "Cmd": [],
            "Entrypoint": "",
            "Image": "sffamily/ulampssh",
            "Labels": {},
            "Volumes": {},
            "WorkingDir": "",
            "NetworkDisabled": false,
            "MacAddress": "",
            "ExposedPorts": {},
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