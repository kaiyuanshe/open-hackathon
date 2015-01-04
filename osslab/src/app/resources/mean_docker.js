{
    "expr_name": "jstrom hackathon_mean",
    "containers": [
        {
            "name": "web",
            "image": "msopentechcn/mean",
            "ports":[{
                "name": "website",
                "port": 3000,
                "host_port": 80,
                "public": true
            },{
                "name": "Deploy",
                "port": 22
            }],
            "command":"/usr/sbin/sshd -D",
            "AttachStdin":false,
            "AttachStdout":true,
            "AttachStderr":true,
            "guacamole": {
                "protocol": "ssh",
                "username": "root",
                "password": "acoman",
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
            "AttachStdin":false,
            "AttachStdout":true,
            "AttachStderr":true,
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