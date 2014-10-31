import web,commands
urls = ('/(.*)', 'index')

'''
As a api service, this class serves as a http server that receive post request from the RestServer
'''
class index:
    def __init__(self):
        pass
    def parse(self,uri):
        pass
    
      
    def POST(self,name):
        #print name
        data = web.input()
        '''
        request:1 or 2, 1 is to create a container, 2 is to shutdown&remove a container
        port: specify the container's port
        image: image
        container_info: specify the info of the container, such as memory, disk, etc.
        '''
        request = data['request']
        port = data['port']
        image = data['image']
        container_info = data['container_info']
        
        #TODO--2
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