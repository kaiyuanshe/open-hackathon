from app import app
from flask.ext.sqlalchemy import SQLAlchemy
from functions import *
from datetime import datetime

app.config["SQLALCHEMY_DATABASE_URI"]= safe_get_config("mysql/connection", "mysql://root:root@localhost/hackathon")
db= SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

class HostServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vm_name = db.Column(db.String(100), unique=True, nullable=False)
    public_dns = db.Column(db.String(50))
    public_cloudvm_port = db.Column(db.Integer)
    private_ip = db.Column(db.String(50), unique=True)
    private_cloudvm_port = db.Column(db.Integer)
    container_count = db.Column(db.Integer, nullable=False)
    container_max_count = db.Column(db.Integer, nullable=False)

    # e,g,:DockerHostServer('oss-docker-vm1', 'osslab1.chinacloudapp.cn', 8001, '10.207.250.79', 80, 0, 100)
    def __init__(self, vm_name, public_dns, public_cloudvm_port, private_ip, private_cloudvm_port, container_count, container_max_count):
        self.vm_name = vm_name
        self.public_dns = public_dns
        self.public_cloudvm_port = public_cloudvm_port
        self.private_ip = private_ip
        self.private_cloudvm_port = private_cloudvm_port
        self.container_count = container_count
        self.container_max_count = container_max_count

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

class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50)) #e.g.trial, real-time-analytics-hackathon
    status = db.Column(db.Integer) #1=running 2=stopped
    create_time = db.Column(db.DateTime)
    last_heart_beat_time = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('experiments', lazy='dynamic'))

    def __init__(self, user, type, status, create_time=None, last_heart_beat_time=None):
        if create_time is None:
            create_time = datetime.utcnow()
        if last_heart_beat_time is None:
            last_heart_beat_time = datetime.utcnow()

        self.user = user
        self.type = type
        self.status = status
        self.create_time = create_time
        self.last_heart_beat_time = last_heart_beat_time

    def __repr__(self):
        return "ResourceServer: {user=%r, type=%s, status=%d, create_time=%r, last_heart_beat_time=%r}" % (
            self.user,
            self.type,
            self.status,
            self.create_time,
            self.last_heart_beat_time
        )

class DockerContainer(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(100), unique=True, nullable=False)
    image= db.Column(db.String(50), nullable=False)
    template= db.Column(db.String(50), nullable=False)
    status= db.Column(db.Integer) # 0=init 1=running 2=stopped 3=removed
    create_time= db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('containers', lazy='dynamic'))

    host_server_id = db.Column(db.Integer, db.ForeignKey('host_server.id'))
    host_server = db.relationship('HostServer', backref=db.backref('containers', lazy='dynamic'))

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    experiment = db.relationship('Experiment', backref=db.backref('containers', lazy='dynamic'))

    def __init__(self, name, user, host_server, experiment, image, template, create_time=None):
        self.name = name
        self.user = user
        self.host_server = host_server
        self.experiment= experiment
        self.image= image
        self.template= template
        self.status= 1
        self.create_time= create_time if create_time is not None else datetime.utcnow()

    def __repr__(self):
        return "ResourceServer: {name=%s, user=%r, host_server=%r, experiment=%r, image=%s, template=%s, status=%d, create_time=%r}" % (
            self.name,
            self.user,
            self.host_server,
            self.experiment,
            self.image,
            self.template,
            self.status,
            self.create_time
        )

class PortBinding(db.Model):
    # for simplicity, the port won't be released until the corresponding container removed(not stopped).
    # that means a port occupied by stopped container won't be allocated to new container. So it's possible to start the
    # container again. And the number of port should be enough since we won't have too many containers on the same VM.
    id= db.Column(db.Integer, primary_key=True)
    vm_public_port= db.Column(db.Integer)
    vm_private_port= db.Column(db.Integer, nullable=False)
    container_port= db.Column(db.Integer, nullable=False)

    host_server_id = db.Column(db.Integer, db.ForeignKey('host_server.id'))
    host_server = db.relationship('HostServer', backref=db.backref('containers', lazy='dynamic'))

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.id'))
    experiment = db.relationship('Experiment', backref=db.backref('containers', lazy='dynamic'))

    container_id = db.Column(db.Integer, db.ForeignKey('docker_container.id'))
    container = db.relationship('DockerContainer', backref=db.backref('port_bindings', lazy='dynamic'))

    def __init__(self, vm_public_port, vm_private_port, container_port, host_server, experiment, container):
        self.vm_public_port = vm_public_port
        self.vm_private_port = vm_private_port
        self.container_port = container_port
        self.host_server = host_server
        self.experiment = experiment
        self.container = container

    def __repr__(self):
        return "ResourceServer: {vm_public_port=%d, vm_private_port=%d, container_port=%d, host_server=%r, experiment=%r, container=%r}" % (
            self.vm_public_port,
            self.vm_private_port,
            self.container_port,
            self.host_server,
            self.experiment,
            self.container
        )
