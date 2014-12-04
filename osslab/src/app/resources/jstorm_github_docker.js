{
    "expr_name": "jstrom hackathon",
    "containers": [
        {
            "name": "jstorm",
            "image": "sffamily/jstorm-base",
            "detach":true,
            "tty": true,
            "stdin_open": true
        },
        {
            "name": "jstorm-api",
            "image": "verdverm/flask",
            "ports":[{
                "name": "flask",
                "port": 5000,
                "host_port": 15001
            }],
            "mnt":["/var/lib/osslab/0e2fe1ee-6ee6-11e4-b166-60eb695c6e39/open-hackathon/jStorm-api/src","/src"],
            "detach":true
        },
        {
            "name": "python-app",
            "image": "verdverm/flask",
            "ports":[{
                "name": "flask",
                "port": 5000,
                "public": true
            }],
            "mnt":["/var/lib/osslab/0e2fe1ee-6ee6-11e4-b166-60eb695c6e39/open-hackathon/app/python-on-flask/src","/src"],
            "detach":true
        },
        {
            "name": "vnc",
            "image": "sffamily/ubuntu-gnome-vnc-eclipse",
            "ports":[{
                "name": "dev",
                "port": 5901
            }],
            "mnt":["/var/lib/osslab/0e2fe1ee-6ee6-11e4-b166-60eb695c6e39/open-hackathon/src","/data"],
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