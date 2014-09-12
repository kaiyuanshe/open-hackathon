from app.database import init_db
from app.database import db_session
from app.models import User

init_db()
u = User('admin' , 'admin@localhost')
db_session.add(u)
db_session.commit()
User.query.all()
