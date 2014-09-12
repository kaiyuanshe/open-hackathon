from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from tables import GuacamoleClientInfo,GuacamoleServerLoad
import constants

DBSession = sessionmaker(autoflush=True,expire_on_commit=False)
DB_CONNECT_STRING = 'mysql+mysqldb://root:******@localhost/******?charset=utf8'

def init_session(CON=DB_CONNECT_STRING):
    global DBSession
    engine = create_engine(CON, echo=False)
    DBSession.configure(bind=engine)

init_session(constants.database_str)