from osslab.src.app.database import init_db
from osslab.src.app.database import db_session
from osslab.src.app.models import User

init_db()
u = User('admin' , 'admin@localhost' , 'test')
db_session.add(u)
db_session.commit()
User.query.all()
