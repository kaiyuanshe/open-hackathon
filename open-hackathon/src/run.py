#!flask/bin/python
from hackathon import app


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=15000, debug=True)