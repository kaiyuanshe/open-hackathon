A service to export RESTFul API to manage docker containers.

# Preconditions
- Python 2.7: [download python](https://www.python.org/downloads/)
- pip: [install pip](http://pip.readthedocs.org/en/latest/installing.html)
- mysql: [download mysql](http://dev.mysql.com/downloads/)
- *windows only*: [visual c++ compiler for python](http://www.microsoft.com/en-us/download/details.aspx?id=44266)
- *windows only*: [install MySQL Connector/C for windows](http://dev.mysql.com/downloads/connector/c/6.0.html#downloads)
- [git](http://git-scm.com/downloads).
- _optional_, you can install [SmartGit]() if you feel uncomfortable about git bash.

# setup
after all the preconditions are met on your dev machine, install the following python libraries via pip.

Or you can simply install all libraries by `pip install -r requirements.txt`.
- `pip install flask`
- `pip install flask-restful`
- `pip install docker-py`
- `pip install gittle`
- `pip install wsgilog`

Note that the list here may not up-to-date. When you see error like `no module named XXX`, that means you need install
the specific lib in the error message, try `pip install XXX` in this case.

# run
change directory to `cloudvm/src` and run `python run.py` to start the flask server.

By default the server will listen on port `8001` and run in debug model. You can edit run.py to listen a different port.

Browse to `http://localhost:8001` to see the welcome page to make sure its ready.