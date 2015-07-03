{
    "expr_name": "sample",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "ssh",
            "image": "42.159.103.213:5000/mono-ssh",
            "ports":[{
                "name": "website",
                "port": 80,
                "host_port": 80,
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
                "password": "acoman",
                "port": 22
            }
        },
        {
            "provider": "docker",
            "name": "gui",
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