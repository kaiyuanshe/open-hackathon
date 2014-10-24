import urllib,urllib2

def postForContainer(url, data): 
    req = urllib2.Request(url) 
    data = urllib.urlencode(data)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor()) 
    response = opener.open(req, data) 
    return response.read() 

def create_container(vm = '',port = -1,image='',container_info=None):
    url = vm
    data = {'request':'1','image':image,'port':port,'container_info':container_info}
    response =postForContainer(url,data)
    if response==None:#failed
        return False
    print response
    return True

def shutdown_container(vm='',port = -1,image = '',container_info=None):
    return False

if __name__=='__main__':
    create_container('http://0.0.0.0:5678', 10000, 'python', None)