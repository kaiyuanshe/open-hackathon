from database import init_db
from database import db_session
from models import User

init_db()
u = User('admin' , 'admin@localhost' , 'test')
db_session.add(u)
db_session.commit()
User.query.all()
