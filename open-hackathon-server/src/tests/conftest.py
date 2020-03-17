import pytest

from hackathon.hmongo.models import User
from hackathon.hmongo.database import add_super_user
from hackathon.hmongo.database import drop_db, setup_db


@pytest.fixture(scope="class")
def user1():
    # return new user named one
    one = User(
        name="test_one",
        nickname="test_one",
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=False)
    one.set_password("test_password")
    one.save()
    return one


@pytest.fixture(scope="class")
def user2():
    # return new user named two
    two = User(
        name="test_two",
        nickname="test_two",
        avatar_url="/static/pic/monkey-32-32px.png",
        is_super=False)
    two.set_password("test_password")
    two.save()
    return two


@pytest.fixture(scope="class")
def admin1():
    # return new admin named one
    return add_super_user("admin_one", "admin_one", "test_password")


def setup_class():
    drop_db()
    setup_db()


def teardown_class():
    drop_db()
