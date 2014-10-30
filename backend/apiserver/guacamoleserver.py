'''
@author: kehl
@contact: t-jikang@microsoft.com
'''
import orm

from xml.etree.ElementTree import ElementTree
from orm.tables import GuacamoleClientInfo,GuacamoleServerLoad
from datetime import datetime
from orm import DBSession
    
def read_config(config_file):
    session = DBSession()
    tree = ElementTree()
    tree.parse(config_file)
    root = tree.getroot()
    server = root.attrib['name']
    server_vm = root.attrib['virtual_machine']
    protocals = root.getchildren()
    acnt = [0,0,0,0]
    cur_datetime = datetime.now()
    t = []
    for protocal in protocals:
        pro_name = protocal.attrib['name']
        clients = protocal.getchildren()
        cnt = 0
        for client in clients:
            cnt+=1
            client_name = client.attrib['name']
            client_host = client[0].text
            client_vm = client[1].text
            guacamoleClientInfo = GuacamoleClientInfo('','',server,client_name,pro_name,client_host,client_vm,0,cur_datetime)
            #t.append(guacamoleClientInfo)
            session.add(guacamoleClientInfo)
        #session.commit()    
        if pro_name=='vnc':
            acnt[0] = cnt
        elif pro_name=='vnc-read-only':
            acnt[1] = cnt
        elif pro_name=='ssh':
            acnt[2] = cnt
        else:
            acnt[3] = cnt
    
    guacamoleServerLoad = GuacamoleServerLoad(server,server_vm,acnt[0],acnt[1],acnt[2],acnt[3],sum(acnt),cur_datetime,0)
    #guacamoleServerLoad.guacamole_client_info = t
    session.add(guacamoleServerLoad)
    session.commit()
    session.close()
        

if __name__=='__main__':
    orm.init_session()
    read_config('/home/kehl/workspace/OSSLab/conf/guacamole_server2.xml')
    