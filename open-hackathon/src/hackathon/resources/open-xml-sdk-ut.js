{
    "expr_name": "jstrom hackathon_ubuntu",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "web",
            "image": "42.159.103.213:5000/mono-ssh",
            "ports":[{
                "name": "website",
                "port": 80,
                "public": true
            },{
                "name": "Deploy",
                "port": 22,
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