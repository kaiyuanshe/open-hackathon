{
    "expr_name": "ampcamp-ud",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "vnc",
            "image": "sffamily/ampcamp5:v3",
            "ports":[{
                "name": "website",
                "port": 80,
                "public": true
            },{
                "name": "Dev",
                "port": 5901,
                "public": true
            },{
                "name": "ampcamp",
                "port": 4040,
                "public": true
            }],
            "AttachStdin":false,
            "AttachStdout":true,
            "AttachStderr":true,
            "tty": true,
            "stdin_open": true,
            "remote": {
                "provider": "guacamole",
                "protocol": "vnc",
                "username": "root",
                "password": "acoman",
                "port": 5901
            }
        }
    ]
}