import web,os
urls = ('/(.*)', 'index')

class index:
    def __init__(self):
        pass
    def parse(self,uri):
        pass
    
    def POST(self,name):
        #print name
        data = web.input()
        request = data['request']
        port = data['port']
        image = data['image']
        container_info = data['container_info']
        
    
    def GET(self,info):
        web.input(info=None)
        #shit=web.ctx.items()
        #print shit
        info = str(info)
        info = info.split('_')
        print info
        client=''
        

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()