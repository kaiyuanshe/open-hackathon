{
    "course_name": "jstrom hackathon",
    "scm" :{
        "provider": "git",
        "repo_name": "flask-example",
        "repo_url":"https://github.com/juniwang/flask-example.git",
        "branch": "master"
    },
    "containers": [
        {
            "name": "web",
            "image": "verdverm/flask",
            "ports":[{
                "name": "flask",
                "port": 5000,
                "public": true
            }],
            "mnt":["%s/src","/src"],
            "mnt2": ["/home/junbo/github/juniwang/flask-example/src", "/src"],
            "detach":true
        },
        {
            "name": "vnc",
            "image": "cannycomputing/dockerfile-ubuntu-gnome",
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