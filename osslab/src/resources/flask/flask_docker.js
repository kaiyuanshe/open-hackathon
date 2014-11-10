{
    "course_name": "python_flask_course",
    "scm" :{
        "provider": "git",
        "repo_name": "flask-example",
        "repo_url":"https://github.com/juniwang/flask-example.git"
    },
    "containers": [
        {
            "name": "web",
            "image": "verdverm/flask",
            "ports":[5000],
            "mnt":["%s/src","/src"],
            "url": "http://localhost:8080/client.xhtml?id=c%2Fpython",
            "detach":true,
            "public":true
        },
        {
            "name": "sshd",
            "image": "rastasheep/ubuntu-sshd:14.04",
            "ports":[22],
            "mnt":["%s/src","/src"],
            "detach":true,
            "guacamole": {
                "protocol": "ssh",
                "username": "root",
                "password": "root",
                "port": 22,
                "hostname": "10.0.2.15"
            }
        }
    ]
}