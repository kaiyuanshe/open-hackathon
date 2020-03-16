import pytest


@pytest.fixture(scope="class")
def user1():
    # return new user named one
    pass


@pytest.fixture(scope="class")
def user2():
    # return new user named two
    pass


@pytest.fixture(scope="class")
def admin1():
    # return new admin named one
    pass
