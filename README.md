LABOSS
======

Open Source Software Laboratory

backend:

	1. Run the backend_install.sh to install all the dependency libraries. If it fails, it may be caused by the network issue, try to change the source list.
	
	2. Then add your personal info to backend/template_constants.py and rename template_constants.py to constants.py
	
	3. If you want to install the mysql server and want this server to be the data layer, then you need to run the database_init.py file with sudo.

====================================================================================
cloudvm:
	
	If you want your vm to be the backend vm which is the host of the containers, you shall just enable the cloudvm package
	
	1. sudo bash ./cloudvm_install.sh
	2. python cloudvm_apiservice.py --port=8080 #any other port is OK
	

	
