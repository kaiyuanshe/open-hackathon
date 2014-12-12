{
    "expr_name": "jstrom hackathon_python",
    "containers": [
        {
            "name": "web",
            "image": "msopentechcn/flask",
            "ports":[{
                "name": "website",
                "port": 5000,
                "public": true
            },{
                "name": "Deploy",
                "port": 22
            }],
            "mnt2":["%s/src","/src"],
            "mnt": ["/home/opentech/github/flask-example/src", "/src"],
            "detach":true,
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