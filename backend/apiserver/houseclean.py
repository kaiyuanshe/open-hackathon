import time,containerservice,constants
from orm import DBSession
from orm.tables  import GuacamoleClientInfo,GuacamoleServerLoad
from datetime import datetime

#init_session()
client_time_limit = constants.client_time_limit
server_time_limit = constants.server_time_limit

def __server_protocol_update(protocol,gain,result):
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

def __str2time(s):
    t = time.strptime(s,'%Y-%m-%d %H:%M:%S')
    latest_active_time = datetime(*t[:6])
    return latest_active_time

def __time_diff(t1,t2):
    seconds = (t1-t2).seconds
    return seconds

'''
'''
def reset_guacamole_client():
    session = DBSession()
    query = session.query(GuacamoleClientInfo)
    #If I can add another condition for query to lock with update, for example, query.filter(GuacamoleClientInfo.guacamole_client_host=='').filter.......
    #Then this process can be more fine-grained
    result = query.filter(GuacamoleClientInfo.status==1).filter(GuacamoleClientInfo.user_info!='').with_lockmode('update').all()
    if result==None:
        return
    cur_time = datetime.now()
    for res in result:
        seconds = __time_diff(cur_time,res.latest_active_timestamp)
        if seconds>=client_time_limit:
            guacamole_client_vm = res.guacamole_client_vm
            guacamole_client_host = res.guacamole_client_host
            image = res.image
            
            res.user_info = ''
            res.status = 0
            res.image = ''
            protocol = res.protocol
            guacamole_server = res.guacamole_server
            query = session.query(GuacamoleServerLoad)
            result = query.filter(GuacamoleServerLoad.guacamole_server == guacamole_server).with_lockmode('update').first()
            result = __server_protocol_update(protocol,-1,result)
            
            signal = containerservice.shutdown_container(guacamole_client_vm,int(guacamole_client_host[guacamole_client_host.index(':')+1:]),image)
            if signal==False:
                #Record this error
                pass
    session.commit()
    session.close()
    
def remove_guacamole_server():
    session = DBSession()
    try:
        query = session.query(GuacamoleServerLoad)
        results = query.filter(GuacamoleServerLoad.server_load==0).all()
        for res in results:
            validate_remove_guacamole_server(res.guacamole_server,res.load_upper_bound)
    except Exception,e:
        print e
    finally:
        session.close()

def validate_remove_guacamole_server(guacamole_server,load_upper_bound):
    session = DBSession()
    try:
        query = session.query(GuacamoleClientInfo)
        results = query.filter(GuacamoleClientInfo.guacamole_server==guacamole_server).filter(GuacamoleClientInfo.status==0).with_lockmode('update').all()
        if len(results)<load_upper_bound:
            raise Exception
        cur_time = datetime.now()
        
        for res in results:
            cur_diff = __time_diff(cur_time, res.latest_active_timestamp)
            if cur_diff<server_time_limit: 
                raise Exception    
        for res in results:
            session.delete(res)
        query = session.query(GuacamoleServerLoad)
        server = query.filter(GuacamoleServerLoad.guacamole_server==guacamole_server).with_lockmode('update').first()
        session.delete(server)
        session.commit()
        return True
    except Exception,e:
        print e
        session.rollback()
        return False
    finally:
        session.close()
        
if __name__=='__main__':
    #reset_guacamole_client()
    remove_guacamole_server()
    #session = DBSession()
    #session.execute('lock tables guacamole_client_info write')
    #time.sleep(100)
    #query = session.query(GuacamoleClientInfo)
    #res = query.filter(GuacamoleClientInfo.protocol=='vnc').with_lockmode('read').first()
    #t='2014-09-02 10:43:55'
    #t2 = __str2time(t)
    #time.sleep(1000)
    #session.commit()
    
        
        
        