import web,commands
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
        
        if request=='1':
            pass
        elif request=='2':
            pass
        else:
            return False#Illegal request
        
        status,output = commands.getstatusoutput('')
        if status!=0:#error
            return False
        return True
        

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()