{
    "expr_name": "jstrom hackathon_ubuntu",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "web",
            "image": "rastasheep/ubuntu-sshd:latest",
            "ports":[{
                "name": "website",
                "port": 80,
                "public": true
            },{
                "name": "Deploy",
                "port": 22
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
                "password": "root",
                "port": 22
            }
        },
        {
            "provider": "docker",
            "name": "vnc",
            "image": "sffamily/ubuntu-gnome-vnc-eclipse",
            "ports":[{
                "name": "Dev",
                "port": 5901
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