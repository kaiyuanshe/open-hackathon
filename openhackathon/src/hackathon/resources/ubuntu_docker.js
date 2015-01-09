{
    "expr_name": "jstrom hackathon_ubuntu",
    "containers": [
        {
            "name": "web",
            "image": "rastasheep/ubuntu-sshd:latest",
            "ports":[{
                "name": "website",
                "port": 80,
                "host_port": 80,
                "public": true
            },{
                "name": "Deploy",
                "port": 22
            }],
            "detach":true,
            "tty": true,
            "stdin_open": true,
            "guacamole": {
                "protocol": "ssh",
                "username": "root",
                "password": "root",
                "port": 22
            }
        },
        {
            "name": "vnc",
            "image": "sffamily/ubuntu-gnome-vnc-eclipse",
            "ports":[{
                "name": "Dev",
                "port": 5901
            }],
            "detach":true,
            "tty": true,
            "stdin_open": true,
            "guacamole": {
                "protocol": "vnc",
                "username": "root",
                "password": "acoman",
                "port": 5901
            }
        }
    ]
}