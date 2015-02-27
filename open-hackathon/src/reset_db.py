from hackathon.database import Base, engine
from setup_db import setup_db

Base.metadata.drop_all(bind=engine)
setup_db()
