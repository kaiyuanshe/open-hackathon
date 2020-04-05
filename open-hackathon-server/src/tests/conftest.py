import pytest

from hackathon.constants import VE_PROVIDER, TEMPLATE_STATUS
from hackathon.hmongo.models import User, Template
from hackathon.hmongo.database import add_super_user


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


@pytest.fixture(scope="class")
def default_template(user1):
    tmpl = Template(
        name="test_default_template",
        provider=VE_PROVIDER.DOCKER,
        status=TEMPLATE_STATUS.UNCHECKED,
        description="old_desc",
        content="",
        template_args={},
        docker_image="ubuntu",
        network_configs=[],
        virtual_environment_count=0,
        creator=user1,
    )
    tmpl.save()
    return tmpl
