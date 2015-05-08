{
    "expr_name": "ampcamp-ut",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "web",
            "image": "sffamily/ampcamp5:v3",
            "ports":[{
                "name": "Tachyon",
                "port": 19999,
                "public": true
            },{
                "name": "Deploy",
                "port": 22,
                "public": true
            },{
                "name": "WebUI",
                "port": 4040,
                "public": true
            }],
            "Env": ["JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/jre/"],
            "command": "/usr/sbin/sshd -D",
            "AttachStdin":false,
            "AttachStdout":true,
            "AttachStderr":true,
            "tty": true,
            "stdin_open": true,
            "remote": {
                "provider": "guacamole",
                "protocol": "ssh",
                "username": "root",
                "password": "acoman",
                "port": 22
            }
        }
    ]
}