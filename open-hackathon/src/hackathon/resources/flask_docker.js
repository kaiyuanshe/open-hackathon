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
                "name": "website",
                "port": 5000,
                "public": true
            },{
                "name": "website",
                "port": 22
            }],
            "mnt2":["%s/src","/src"],
            "mnt": ["/home/opentech/github/flask-example/src", "/src"],
            "AttachStdin":false,
            "AttachStdout":true,
            "AttachStderr":true,
            "guacamole": {
                "protocol": "ssh",
                "username": "root",
                "password": "root",
                "port": 22
            }
        },
        {
            "name": "sshd",
            "image": "rastasheep/ubuntu-sshd:14.04",
            "ports":[{
                "name": "Dev",
                "port": 22
            }],
            "mnt2":["%s/src","/src"],
            "mnt": ["/home/opentech/github/flask-example/src", "/src"],
            "AttachStdin":false,
            "AttachStdout":true,
            "AttachStderr":true,
            "guacamole": {
                "protocol": "ssh",
                "username": "root",
                "password": "root",
                "port": 22
            }
        }
    ]
}