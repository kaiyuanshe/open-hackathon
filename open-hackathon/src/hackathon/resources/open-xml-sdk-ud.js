{
    "expr_name": "jstrom hackathon_ubuntu",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "vnc",
            "image": "42.159.103.213:5000/mono",
            "ports":[{
                "name": "website",
                "port": 80,
                "public": true
            },{
                "name": "Dev",
                "port": 5901,
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