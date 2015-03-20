{
    "expr_name": "kaiyuanshe-ud",
    "virtual_environments": [
        {
            "provider": "docker",
            "name": "ubuntu",
            "image": "sffamily/ubuntu-gnome-vnc-eclipse",
            "ports":[{
                "name": "website",
                "port": 80,
                "public": true
            },{
                "name": "vnc",
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