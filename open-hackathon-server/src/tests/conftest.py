import pytest

from hackathon.hmongo.models import User
from hackathon.hmongo.database import add_super_user
from hackathon.hmongo.database import drop_db, setup_db


@pytest.fixture(scope="function")
def user1():
    # return new user named one
    one = User(
        name="test_one",
        nickname="test_one",
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=False)
    one.set_password("test_password")

    User.objects(name="test_one").update_one(__raw__={"$set": one.to_mongo().to_dict()}, upsert=True)
    return one


@pytest.fixture(scope="function")
def user2():
    # return new user named two
    two = User(
        name="test_two",
        nickname="test_two",
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=False)
    two.set_password("test_password")

    User.objects(name="test_two").update_one(__raw__={"$set": two.to_mongo().to_dict()}, upsert=True)
    return two


@pytest.fixture(scope="function")
def admin1():
    # return new admin named one
    return add_super_user("admin_one", "admin_one", "test_password")


def setup_class():
    drop_db()
    setup_db()


def teardown_class():
    drop_db()
