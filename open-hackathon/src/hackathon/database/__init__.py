import sys

sys.path.append("..")
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from db_adapters import SQLAlchemyAdapter
from hackathon.functions import safe_get_config


engine = create_engine(safe_get_config("mysql.connection", "mysql://root:root@localhost/hackathon"),
                       convert_unicode=True,
                       pool_size=50,
                       max_overflow=100)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
db_adapter = SQLAlchemyAdapter(db_session)
