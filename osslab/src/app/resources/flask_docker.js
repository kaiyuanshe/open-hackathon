{
    "expr_name": "python_on_flask",
    "scm2" :{
        "provider": "git",
        "repo_name": "flask-example",
        "repo_url":"https://github.com/juniwang/flask-example.git",
        "branch": "master"
    },
    "containers": [
        {
            "name": "web",
            "image": "msopentechcn/flask",
            "ports":[{
                "name": "flask",
                "port": 5000,
                "public": true
            }],
            "mnt2":["%s/src","/src"],
            "mnt": ["/home/opentech/github/flask-example/src", "/src"],
            "detach":true
        },
        {
            "name": "sshd",
            "image": "rastasheep/ubuntu-sshd:14.04",
            "ports":[{
                "name": "ssh",
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
        }
    ]
}