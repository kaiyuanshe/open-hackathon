from app import app
from flask.ext.sqlalchemy import SQLAlchemy
from functions import *

app.config["SQLALCHEMY_DATABASE_URI"]= safe_get_config("mysql/connection", "mysql://root:root@localhost/hackathon")
db= SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(80), unique=True)
    email =db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username=username
        self.email=email

    def __repr__(self):
        return '<User %r>' % self.username

class DockerHostServer(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    vm_name= db.Column(db.String(100), unique=True)
    public_dns= db.Column(db.String(50))
    public_cloudvm_port= db.Column(db.Integer)
    private_ip= db.Column(db.String(50), unique=True)
    private_cloudvm_port= db.Column(db.Integer)
    container_count= db.Column(db.Integer)
    container_max_count= db.Column(db.Integer)

    # e,g,:DockerHostServer('oss-docker-vm1', 'osslab1.chinacloudapp.cn', 8001, '10.207.250.79', 80, 0, 100)
    def __init__(self, vm_name, public_dns, public_cloudvm_port, private_ip, private_cloudvm_port, container_count, container_max_count):
        self.vm_name= vm_name
        self.public_dns= public_dns
        self.public_cloudvm_port= public_cloudvm_port
        self.private_ip= private_ip
        self.private_cloudvm_port= private_cloudvm_port
        self.container_count= container_count
        self.container_max_count= container_max_count

    def __repr__(self):
        return "ResourceServer: {vmname=%s, public_dns=%s, public_cloudvm_port=%d, private_ip=%s, private_cloudvm_port=%s, container_count=%d, container_max_count=%d}" % (
            self.vm_name,
            self.public_dns,
            self.public_cloudvm_port,
            self.private_ip,
            self.private_cloudvm_port,
            self.container_count,
            self.container_max_count
        )

class DockerContainer(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    vm_name= db.Column(db.String(100))
    user_id= db.Column(db.String(50))
    container_name= db.Column(db.String(100), unique=True)
    container_group_id= db.Column(db.String(50))
    image= db.Column(db.String(50))
    template= db.Column(db.String(50))
    create_time= db.Column(db.DateTime)

    def __init__(self, vm_name, user_id, container_name, container_group_id, image, template, create_time):
        self.vm_name= vm_name
        self.user_id= user_id
        self.container_name= container_name
        self.container_group_id= container_group_id
        self.image= image
        self.template= template
        self.create_time= create_time

    def __repr__(self):
        return "ResourceServer: {vmname=%s, user_id=%s, container_name=%s, container_group_id=%s, image=%s, template=%s, create_time=%r}" % (
            self.vm_name,
            self.user_id,
            self.container_name,
            self.container_group_id,
            self.image,
            self.template,
            self.create_time
        )

class ContainerPort(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    vm_name= db.Column(db.String(100))
    container_name= db.Column(db.String(100))
    vm_public_port= db.Column(db.Integer)
    vm_private_port= db.Column(db.Integer)
    container_port= db.Column(db.Integer)

    def __init__(self, vm_name, container_name, vm_public_port, vm_private_port, container_port):
        self.vm_name= vm_name
        self.container_name= container_name
        self.vm_public_port= vm_public_port
        self.vm_private_port= vm_private_port
        self.container_port= container_port

    def __repr__(self):
        return "ResourceServer: {vmname=%s, user_id=%s, container_name=%s, container_group_id=%s, image=%s, template=%s, create_time=%r}" % (
            self.vm_name,
            self.user_id,
            self.container_name,
            self.container_group_id,
            self.image,
            self.template,
            self.create_time
        )

if __name__ == "__main__":
    # initialize db tables
    # make sure database and user correctly created in mysql
    db.create_all()