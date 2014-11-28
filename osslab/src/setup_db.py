from app.database import db

# initialize db tables
# make sure database and user correctly created in mysql
db.create_all()
