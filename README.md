LABOSS
======

Open Source Software Laboratory.

For developers, you must start both osslab and cloudvm locally. Also some test data are required.

- start osslab locally, please follow detail instructions in `osslab` directory.
- start cloudvm locally, please follow detail instructions in `cloudvm` directory.
- change directory to `<src_root_on_your_machine>\osslab\src`, edit and run `create_test_data.py` to create test data.


====================================================================================

osslab:

the site that includes features like UI, login and resource management

====================================================================================

cloudvm:

a service run in background that help checkout/checkin source code, manage guacamole configuration and talk with docker daemon occasionally.

====================================================================================

deploy:

deploy script to deploy osslab and cloudvm as well as some scripts to integrate with CI tools like Jenkins.