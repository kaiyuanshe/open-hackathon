LABOSS
======

Open Source Software Laboratory

backend:

	1. Run the backend_install.sh to install all the dependency libraries. If it fails, it may be caused by the network issue, try to change the source list.
	
	2. Then add your personal info to backend/template_constants.py and rename template_constants.py to constants.py
	
	3. If you want to install the mysql server and want this server to be the data layer, then you need to run the database_init.py file with sudo. And if you want your mysql server can be accessed by other host, you shall config the mysql server.

====================================================================================
cloudvm:
	
	If you want your vm to be the backend vm which is the host of the containers, you shall just enable the cloudvm package
	
	1. sudo bash ./cloudvm_install.sh
	2. python cloudvm_apiservice.py --port=8080 #any other port is OK
	
========= 2014/10/31 check out date ===========
接下来的工作：
1.	Guacamole config文件的设置以及create虚拟机时端口的配置分配情况
2.	在cloudvm/cloudvm_apiservice中需要将docker的启动和删除工作的命令完成
3.	Unittest
4.	Azureservices中的函数和constants.py下的一些配置文件可能会根据azureservice包中接口的改变而需要更改
	
