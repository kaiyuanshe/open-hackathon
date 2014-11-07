{
    "course_name": "python_flask_course",
    "containers": [
        {
            "name": "web",
            "host": "localhost:8001",
            "image": "verdverm/flask",
            "ports":[15001, 5000],
            "mnt":["%s/src","/src"],
            "url": "http://localhost:8080/client.xhtml?id=c%2Fpython",
            "description" : "flask based web server",
            "detach":true,
            "scm" :{
                "provider": "git",
                "repo_name": "flask-example",
                "repo_url":"https://github.com/juniwang/flask-example.git"
             }
        },
        {
            "name": "database",
            "host": "localhost:8001",
            "image": "mysql:latest",
            "ports":[13306,3306],
            "environments": {
                "MYSQL_ROOT_PASSWORD": "1qazXSW@"
            },
            "detach":true,
            "url": "http://localhost:8080/",
            "description" : "mysql database"
        }
    ],
    "guacamole":{
        "container":{
            "name": "guacamole",
            "host": "localhost:8001",
            "image": "hall/guacamole",
            "ports":[9080, 8080],
            "mnt":["/tmp/guacamole/","/etc/guacamole"],
            "url": "http://localhost:8080",
            "description" : "guacamole server",
            "detach":true
        }
    },
    "show_url":"http://localhost:15000"
}