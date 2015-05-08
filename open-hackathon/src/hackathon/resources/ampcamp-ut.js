{
    "expr_name": "ampcamp-ut",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "web",
            "image": "sffamily/ampcamp5:v2",
            "ports":[{
                "name": "website",
                "port": 80,
                "public": true
            },{
                "name": "Deploy",
                "port": 22,
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
                "protocol": "ssh",
                "username": "root",
                "password": "acoman",
                "port": 22
            }
        }
    ]
}