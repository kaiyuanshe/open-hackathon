{
    "course_name": "python_flask_course",
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
            "detach":true
        },
        {
            "name": "sshd",
            "image": "rastasheep/ubuntu-sshd:14.04",
            "ports":[{
                "name": "ssh",
                "port": 22
            }],
            "mnt":["%s/src","/src"],
            "detach":true,
            "guacamole": {
                "protocol": "ssh",
                "username": "root",
                "password": "root",
                "port": 22
            }
        }
    ]
}