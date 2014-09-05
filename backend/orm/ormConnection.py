'''
def activate(user_id):
    orm = ORMConnection()
    session = orm.getSession()
    query=session.query(GuacamoleClientInfo)
    temp = query.filter(GuacamoleClientInfo.user_info==user_id).first()
    if temp==None:
        return
    if temp.status_info==0:
        temp.status_info = 1
    temp.latest_active_timestamp = datetime.now()
    session.commit()

def shutdown(user_lab_id):
    orm = ORMConnection()
    session = orm.getSession()
    query=session.query(GuacamoleClientInfo)
    temp = query.filter(GuacamoleClientInfo.user_info==user_lab_id).first()
    if temp==None:
        return
    temp.status_info = 0
    session.commit()  

def findConnection(user_lab):
    orm = ORMConnection()
    session = orm.getSession()
    query=session.query(GuacamoleClientInfo)
    temp = query.filter(GuacamoleClientInfo.user_info==user_lab).first()
    if temp!=None:
        temp.status=1
        session.commit()
        return temp.guacamole_client
    return None

def delConnection(user_lab):
    orm = ORMConnection()
    session = orm.getSession()
    query=session.query(GuacamoleClientInfo)
    temp = query.filter(GuacamoleClientInfo.user_info==user_lab).first()
    if temp!=None:
        temp.status=0
        temp.user_info=''
        res = temp.guacamole_server
        session.commit()
        query = session.query(GuacamoleServerLoad)
        temp = query.filter(GuacamoleServerLoad.guacamole_server==res).first()
        if temp!=None:
            temp.count = temp.count-1
            if temp.count==0:
                remove_guacamole_server(temp.guacamole_server)
            
        session.commit()
'''

