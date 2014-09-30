import containerservice,constants
from datetime import datetime
from xml.etree.ElementTree import ElementTree
from orm.tables import GuacamoleClientInfo, GuacamoleServerLoad
from orm import DBSession



'''
@author: kehl
@contact: t-jikang@microsoft.com
@version: 0.0
'''

def server_protocol_update(protocol,gain,result):
    if protocol=='ssh':
        result.ssh_count -= gain
    elif protocol=='vnc':
        result.vnc_count -= gain
    elif protocol=='vnc-readonly':
        result.vnc_readonly_count -= gain
    else:
        result.rdp_count -= gain
    result.server_load += gain
    if result.server_load==0:
        result.zero_load_timestamp = datetime.now()
    return result

def heart_beat(client_id, image):
    """Receive heart beat signal
    
    When a heart beat signal is received, the latest_active_timestamp of the record in database is updated
    """
    session = DBSession()
    try:
        query = session.query(GuacamoleClientInfo) 
        result = query.filter(GuacamoleClientInfo.user_info == client_id).filter(GuacamoleClientInfo.image == image).with_lockmode('update').first()
        if result != None:
            result.status = 1
            result.latest_active_timestamp = str(datetime.now())
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()
    
def shutdown_guacamole_client(client_id, image,protocol,mylog):
    guacamole_client_host,guacamole_client_vm = cancel_guacamole_client(client_id, image, protocol)
    if guacamole_client_host==None:
        return
    signal = containerservice.shutdown_container(guacamole_client_vm,int(guacamole_client_host[guacamole_client_host.index(':')+1:]),image)
    if signal==False:
        mylog.info("shutdown a container failed...")
        pass
    
def get_guacamole_client(client_id, image,protocol,mylog):
    session = DBSession()
    guacamole_client = None
    try:
        query = session.query(GuacamoleClientInfo) 
        result = query.filter(GuacamoleClientInfo.user_info == client_id).filter(GuacamoleClientInfo.image == image).with_lockmode('update').first()
        if result != None:
            if result.status == 0:
                result.status = 1
            result.latest_active_timestamp = str(datetime.now())
            guacamole_server = result.guacamole_server
            guacamole_client_name = result.guacamole_client_name
            guacamole_client = guacamole_server+'client.xhtml?id=c/'+guacamole_client_name
            session.commit()
        else:
            session.commit()
            res = establish_guacamole_client(session,client_id, image,protocol)
            if res != None:
                guacamole_client = res
            else:
                create_guacamole_server(session,client_id, image,protocol)
                guacamole_client = get_guacamole_client(client_id, image,protocol,mylog)
    except Exception,e:
        session.rollback()
        print e
    finally:
        session.close()
        return guacamole_client

def apply_guacamole_client(session,client_id,image,protocol = None):
    guacamole_client=None
    guacamole_client_host = None
    guacamole_client_vm = None
    try:
        query = session.query(GuacamoleClientInfo)
        #TODO(): if the protocol is None, then I should specify the protocol with my map or DB.
        if protocol == None:
            result = query.filter(GuacamoleClientInfo.user_info == '').filter(GuacamoleClientInfo.image == '').with_lockmode('update').first()
        else:
            result = query.filter(GuacamoleClientInfo.user_info == '').filter(GuacamoleClientInfo.image == '').filter(GuacamoleClientInfo.protocol == protocol).with_lockmode('update').first()
        if result != None:               
            
            result.user_info = client_id
            result.image = image
            result.status = 1
            result.latest_active_timestamp = str(datetime.now())
            guacamole_server = result.guacamole_server
            guacamole_client_name = result.guacamole_client_name
            guacamole_client_host = result.guacamole_client_host
            guacamole_client_vm = result.guacamole_client_vm
            protocol = result.protocol
            query = session.query(GuacamoleServerLoad)
            result = query.filter(GuacamoleServerLoad.guacamole_server==guacamole_server).with_lockmode('update').first()
            
            if result==None:
                pass
            
            result = server_protocol_update(protocol, 1 , result)
            session.commit()
            guacamole_client = guacamole_server+'client.xhtml?id=c/'+guacamole_client_name
    except Exception:
        print 'apply a guacamole client failed...'
        session.rollback()
    finally:
        return guacamole_client,guacamole_client_host,guacamole_client_vm
    
def cancel_guacamole_client(client_id,image,protocol=None):
    session = DBSession()
    guacamole_client_host = None
    guacamole_client_vm = None
    try:
        query = session.query(GuacamoleClientInfo)
        result = query.filter(GuacamoleClientInfo.user_info == client_id).filter(GuacamoleClientInfo.image == image).filter(GuacamoleClientInfo.protocol == protocol).with_lockmode('update').first()
        if result != None:               
            result.user_info = ''
            result.image = ''
            result.status = 0
            guacamole_server = result.guacamole_server
            guacamole_client_host = result.guacamole_client_host
            guacamole_client_vm = result.guacamole_client_vm
            
            query = session.query(GuacamoleServerLoad)
            result = query.filter(GuacamoleServerLoad.guacamole_server==guacamole_server).with_lockmode('update').first()
            if result==None:
                pass
            
            result = server_protocol_update(protocol, -1 , result)
            session.commit()
    except:
        print 'cancel a guacamole client failed...'
        session.rollback()
    finally:
        session.close()
        return guacamole_client_host,guacamole_client_vm

def establish_guacamole_client(session,client_id, image, protocol=None):
    guacamole_client,guacamole_client_host,guacamole_client_vm = apply_guacamole_client(session,client_id,image,protocol)
    if guacamole_client==None:
        return guacamole_client
    signal = containerservice.create_container(vm = guacamole_client_vm,port = int(guacamole_client_host[guacamole_client_host.index(':')+1:]),image=image)
    if signal==True:
        return guacamole_client
    else:
        guacamole_client = 'Initialize '+image + ' failed...'
        cancel_guacamole_client(client_id, image, protocol)
        return guacamole_client
    
        
'''
    When creating a new guacamole server, there should be a config file there, or maybe just generated automatically
    But does it need to be a method in the class RestServer?
'''
def create_guacamole_server(session,client_id,image,protocol):
    try:
        query = session.query(GuacamoleClientInfo)
        result = query.filter(GuacamoleClientInfo.user_info == '').filter(GuacamoleClientInfo.image == '').filter(GuacamoleClientInfo.protocol==protocol).first()#there is idle guacamole client        
        if result != None:
            session.close()
            return
        else:
            #print client_id +'_'+ image+'_' + protocol + '_create_guacamole_server'
            
            #TODO(): new a Guacamole Server, config file name should be specified. And the read_config() here is the lowest efficient part in the lock mode,
            #so this part is moved out of the lock mode 
            guacamole_server = read_config(constants.guacamole_config_path)
            session.execute('LOCK TABLES guacamole_client_info WRITE,guacamole_server_load WRITE')
            session.add(guacamole_server)
            session.commit()
    except Exception,e:
        print e
        session.rollback()
    finally:
        session.execute('UNLOCK TABLES')
        #session.close()
    

def read_config(config_file):
    tree = ElementTree()
    tree.parse(config_file)
    root = tree.getroot()
    server = root.attrib['name']
    server_vm = root.attrib['virtual_machine']
    protocals = root.getchildren()
    acnt = [0,0,0,0]
    cur_datetime = datetime.now()
    guacamole_client_list=[]
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
            guacamole_client_list.append(guacamoleClientInfo)
        if pro_name=='vnc':
            acnt[0] = cnt
        elif pro_name=='vnc-read-only':
            acnt[1] = cnt
        elif pro_name=='ssh':
            acnt[2] = cnt
        else:
            acnt[3] = cnt
    
    guacamoleServerLoad = GuacamoleServerLoad(server,server_vm,acnt[0],acnt[1],acnt[2],acnt[3],sum(acnt),cur_datetime,0)
    guacamoleServerLoad.guacamole_client_info = guacamole_client_list
    return guacamoleServerLoad