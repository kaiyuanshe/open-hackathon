from mongoengine import connect

from hackathon.hmongo.models import User
from hackathon.util import safe_get_config

mongodb_host = safe_get_config("mongodb.host", "localhost")
mongodb_port = safe_get_config("mongodb.port", 27017)
ohp_db = safe_get_config("mongodb.database", "hackathon")

# mongodb client
client = connect(ohp_db, host=mongodb_host, port=mongodb_port)

# mongodb collection for OHP, authentication disabled for now.
db = client[ohp_db]


def drop_db():
    client.drop_database(ohp_db)


def setup_db():
    """Initialize db tables

    make sure database and user correctly created in db
    in case upgrade the table structure, the origin table need be dropped firstly
    """
    # init REQUIRED db data.

    # reserved user is deleted, may not need in mongodb implementation

    # default super admin


def add_super_user(name, nickname, password):
    admin = User(
        name=name,
        nickname=nickname,
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=True)
    admin.set_password(password)

    User.objects(name=name).update_one(__raw__={"$set": admin.to_mongo().to_dict()}, upsert=True)
    return admin
