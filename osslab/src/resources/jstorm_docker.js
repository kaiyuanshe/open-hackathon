{
    "course_name": "jstrom hackathon",
    "scm" :{
        "provider": "git",
        "repo_name": "open-hackathon",
        "repo_url":"https://github.com/msopentechcn/open-hackathon.git",
        "branch": "master"
    },
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
            "mnt":["%s/jStorm-api/src","/src"],
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
            "mnt":["%s/app/python-on-flask/src","/src"],
            "detach":true
        },
        {
            "name": "vnc",
            "image": "sffamily/ubuntu-gnome-vnc-eclipse",
            "ports":[{
                "name": "dev",
                "port": 5901
            }],
            "mnt":["%s/src","/data"],
            "mnt2": ["/home/junbo/github/juniwang/flask-example/src", "/data"],
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