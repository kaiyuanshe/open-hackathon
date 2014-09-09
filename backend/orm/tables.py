from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String,Boolean,DateTime
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class GuacamoleClientInfo(Base):
    __tablename__='guacamole_client_info'
    
    id = Column(Integer,primary_key=True)
    user_info = Column(String(50),index = True)#can be empty
    image = Column(String(20),index = True)#can be empty
    guacamole_server = Column(String(50),ForeignKey('guacamole_server_load.guacamole_server'),index = True)
    guacamole_client_name=Column(String(30))
    protocol=Column(String(15),index = True)
    guacamole_client_host = Column(String(50))
    guacamole_client_vm = Column(String(50))
    status = Column(Boolean)
    latest_active_timestamp=Column(DateTime)
    
    
    def __init__(self,user_info='',image = '',guacamole_server='',guacamole_client_name='',protocol='',guacamole_client_host = '',guacamole_client_vm='',status=0,latest_active_timestamp=''):
        self.user_info = user_info
        self.image = image
        self.guacamole_server = guacamole_server
        self.guacamole_client_name = guacamole_client_name
        self.protocol = protocol
        self.guacamole_client_host = guacamole_client_host
        self.guacamole_client_vm = guacamole_client_vm
        self.status = status
        self.latest_active_timestamp = latest_active_timestamp
    
    def __repr__(self):
        return "<GuacamoleClientInfo('%s','%s','%s','%s','%s','%s',%s','%s','%s')>" %(self.user_info,
                                                                             self.image,
                                                                             self.guacamole_server,
                                                                             self.guacamole_client_name,
                                                                             self.protocol,
                                                                             self.guacamole_client_host,
                                                                             self.guacamole_client_vm,
                                                                             str(self.status),
                                                                             str(self.latest_active_timestamp)
                                                                             )


class GuacamoleServerLoad(Base):
    __tablename__='guacamole_server_load'
    id=Column(Integer,primary_key=True)
    guacamole_server = Column(String(50),index = True,unique=True)
    guacamole_client_info = relationship('GuacamoleClientInfo',backref='guacamole_server_load')
    guacamole_server_vm = Column(String(50))
    vnc_count = Column(Integer)#load 
    vnc_readonly_count = Column(Integer)
    ssh_count = Column(Integer)
    rdp_count = Column(Integer)
    load_upper_bound = Column(Integer)
    zero_load_timestamp=Column(DateTime)
    server_load = Column(Integer,index = True)#total available count, if it is zero then this guacamole server may should be removed
    
    def __init__(self,guacamole_server,guacamole_server_vm,vnc_count,vnc_readonly_count,ssh_count,rdp_count,load_upper_bound,zero_load_timestamp,server_load):
        self.guacamole_server = guacamole_server
        self.guacamole_server_vm = guacamole_server_vm
        self.vnc_count = vnc_count
        self.vnc_readonly_count = vnc_readonly_count
        self.ssh_count = ssh_count
        self.rdp_count = rdp_count
        self.load_upper_bound = load_upper_bound
        self.zero_load_timestamp = zero_load_timestamp
        self.server_load = server_load
    
    def __repr__(self):
        return "<GuacamoleServerLoad('%s','%s','%s','%s',%s','%s','%s','%s')>" %(self.guacamole_server,
                                                                        self.guacamole_server_vm,
                                                                        str(self.vnc_count),
                                                                        str(self.vnc_readonly_count),
                                                                        str(self.ssh_count),
                                                                        str(self.rdp_count),
                                                                        str(self.zero_load_timestamp),
                                                                        str(self.server_load),
                                                                        )

if __name__=='__main__':
    engine = create_engine('mysql+mysqldb://root:******@localhost/******?charset=utf8', echo=False)#DB path
    Base.metadata.create_all(engine)
    engine.dispose()
    