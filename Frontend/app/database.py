from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

url = 'mysql://root:fdkiller2011@localhost/abc'
engine = create_engine(url,convert_unicode = True,echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
#Base.metadata.create_all(bind=engine)
#session = sessionmaker(bind=engine)
#session.execute('create database User')
#session.execute('use abc')

def init_db():
	import models
	Base.metadata.create_all(bind=engine,checkfirst=False)

#init_db()
