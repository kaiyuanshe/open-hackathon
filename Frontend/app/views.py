from flask import render_template, flash, redirect,request
from app import app
import httplib
import urllib
import json
import uuid
from database import init_db
from database import db_session
from models import User
#from forms import LoginForm

def add_head_href(head,href):
	arr = href.split('href="')
	href = ('href="' + head).join(arr)
	arr = href.split('src="')
	href = ('src="' + head).join(arr)
	return href

@app.route('/')
@app.route('/index')
def index():
        return render_template("index.html")
@app.route('/linux')
def linux():
	return render_template("linux.html")
@app.route('/windows')
def windows():
	return render_template("windows.html")
@app.route('/paper')
def paper():
	return render_template("paper.html")
@app.route('/paper2')
def paper22():
	return render_template("paper2.html")
@app.route('/test')
def test():
	return render_template("test.html")
@app.route('/google')
def google():
	return render_template("google.html")
@app.route('/github')
def github():
	code = request.args.get('code')
	url = '/login/oauth/access_token?client_id=0eded406cf0b3f83b181&client_secret=3c81babd71d0cf60db3362261d42b4ce6b199538&redirect_uri=http://osslab.chinacloudapp.cn:5080/github&code=' + code
	conn = httplib.HTTPSConnection('github.com')
	conn.request('GET',url)
	httpres = conn.getresponse()
	url_ori = httpres.read()
	start = url_ori.index('=')
        end = url_ori.index('&')
        #Str = request.query_string
        access_token = url_ori[start+1:end]
        url = '/user?access_token=' + access_token
        conn = httplib.HTTPSConnection('api.github.com')
        conn.request('GET',url,'',{'user-agent':'flask'})
	#conn.putheader('User-Agent','flask')
        httpres = conn.getresponse()
	info = json.loads(httpres.read())
	name = 'github' + str(info['id'])
	uid = str(uuid.uuid3(uuid.NAMESPACE_DNS,name))
	query = db_session.query(User)
	result = query.filter(User.uid == uid).first()
	if (result == None):
		u = User(info['login'],uid,'github')
		db_session.add(u)
		db_session.commit()
	return render_template("github.html",iden=info['id'],name=info['login'])
	#return render_template("github.html",iden=httpres.read(),name='bbb')
@app.route('/renren')
def renren():
	url_ori = request.url
	#if (url.ori.find('access_token') < 0) return render_template("renren.html",iden=url_ori,name='bb')
	if (len(url_ori)<50):
		return render_template("renren.html",iden=url_ori,name='bb')
	start = url_ori.index('=')
	end = url_ori.index('&')
	#Str = request.query_string
	access_token = url_ori[start+1:end]
	url = '/v2/user/get?access_token=' + access_token
	conn = httplib.HTTPSConnection('api.renren.com')
	conn.request('GET',url)
	httpres = conn.getresponse()
	#info = httpres.read()
	info = json.loads(httpres.read())
	name = 'renren' + str(info['response']['id'])
	uid = str(uuid.uuid3(uuid.NAMESPACE_DNS,name))
	query = db_session.query(User)
	result = query.filter(User.uid == uid).first()
	#result = session.query(User).filter(User.uid == uid).all()
	if (result == None):
		u = User(info['response']['name'],uid,'renren')
		db_session.add(u)
		db_session.commit()
	#info = Str
	#return render_template("renren.html")
	#return render_template("renren.html",iden=url_ori,name='cc')
	return render_template("renren.html",iden = info['response']['id'],name=info['response']['name'])
@app.route('/iframe')
def iframe():
	url = '/guacamole/client.xhtml?id=c%2FContainer%201'
	conn = httplib.HTTPConnection('ossdocker.chinacloudapp.cn')
	conn.request('GET',url)
	httpres = conn.getresponse()
	tot = httpres.read()
	tot = add_head_href('http://ossdocker.chinacloudapp.cn/guacamole/',tot)
	head_s = tot.find('<head>')+6
	head_t = tot.find('</head>')
	headload = tot[head_s:head_t]
	content_s = tot.find('<body>') + 6
	content_t = tot.find('</body>')
	content = tot[content_s:content_t]
	return tot
@app.route('/test_ice')
def test_ice():
	return render_template("test_ice.html")
@app.route('/test_ice1')
def test_ice1():
	return render_template("test_ice1.html")
@app.route('/test_ice2')
def test_ice2():
        return render_template("test_ice2.html")
@app.route('/test_ice3')
def test_ice3():
        return render_template("test_ice3.html")
@app.route('/test_ice4')
def test_ice4():
        return render_template("test_ice4.html")
@app.route('/test_ice5')
def test_ice5():
        return render_template("test_ice5.html")
@app.route('/test_ice6')
def test_ice6():
        return render_template("test_ice6.html")
@app.route('/test_ice7')
def test_ice7():
        return render_template("test_ice7.html")
@app.route('/test_ice8')
def test_ice8():
        return render_template("test_ice8.html")
@app.route('/test_ice9')
def test_ice9():
        return render_template("test_ice9.html")
@app.route('/test_ice10')
def test_ice10():
        return render_template("test_ice10.html")
@app.route('/test_ice11')
def test_ice11():
        return render_template("test_ice11.html")
@app.route('/test_ice12')
def test_ice12():
        return render_template("test_ice12.html")
@app.route('/test_ice13')
def test_ice13():
        return render_template("test_ice13.html")
@app.route('/test_ice14')
def test_ice14():
        return render_template("test_ice14.html")
@app.route('/test_ice15')
def test_ice15():
        return render_template("test_ice15.html")
@app.route('/test_ice16')
def test_ice16():
        return render_template("test_ice16.html")
@app.route('/test_ice17')
def test_ice17():
        return render_template("test_ice17.html")
@app.route('/test_ice18')
def test_ice18():
        return render_template("test_ice18.html")
@app.route('/test_ice19')
def test_ice19():
        return render_template("test_ice19.html")
@app.route('/test_ice20')
def test_ice20():
        return render_template("test_ice20.html")
