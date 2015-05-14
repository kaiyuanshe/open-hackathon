{
    "expr_name": "kaiyuanse-ubuntu-terminal",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "ubuntu",
            "image": "sffamily/ulampssh",
            "ports":[{
                "name": "website",
                "port": 80,
                "public": true
            },{
                "name": "ssh",
                "port": 22,
                "public": true
            },{
                "name": "mysql",
                "port": 3306,
                "public": false
            }],
            "AttachStdin":false,
            "AttachStdout":true,
            "AttachStderr":true,
            "tty": true,
            "Env": ["ROOT_PASS=acowoman"],
            "stdin_open": true,
            "remote": {
                "provider": "guacamole",
                "protocol": "ssh",
                "username": "root",
                "password": "acowoman",
                "port": 22
            }
        }
    ]
}
