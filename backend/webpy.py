import web,orm,constants
import apiserver.restserver as restserver
from backendlogger.logger import Logger
urls = ('/(.*)', 'index')
#orm.init_session(constants.database_str)
'''
Rest Server
'''

class index:
    def __init__(self):
        self.mylog = web.ctx.environ['wsgilog.logger']
        
    def parse(self,uri):
        pass
    
    def POST(self,name):
        print name
        data = web.input()
        request_type = data['request']
        client_id = data['client_id']
        image = data['image']
        protocol = data['protocol']
        if request_type=='1':
            client = restserver.get_guacamole_client(client_id,image,protocol,self.mylog)
            return client
        elif request_type=='2':
            restserver.shutdown_guacamole_client(client_id,image,protocol,self.mylog)
            return None
        else:
            return 'Illegal Request...'
    
    def GET(self,info):
        web.input(info=None)
        #shit=web.ctx.items()
        #print shit
        info = str(info)
        info = info.split('_')
        print info
        client=''
        if info[0]=='1':#ask for a guacamole server
            client = restserver.get_guacamole_client(info[1],info[2],info[3],self.mylog)           
        elif info[0]=='2':#heart beat
            restserver.heart_beat(info[1],info[2])
        elif info[0]=='3':#reset guacamole client
            restserver.shutdown_guacamole_client(info[1], info[2],info[3],self.mylog)
        return client

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run(Logger)