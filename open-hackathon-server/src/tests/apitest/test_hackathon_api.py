from . import ApiTestCase


class TestHackathonApi(ApiTestCase):
    def test_list_hackathons(self):
        pass

    def test_get_hackathon_statistics(self):
        pass

    def test_get_hackathon_registered_users(self):
        pass

    def test_get_hackathon_tags(self):
        pass

    def test_like_unlike_hackathon(self):
        pass


class TestParticipantApi(ApiTestCase):
    def test_registration(self):
        pass

    def test_list_participated_hackathon(self):
        pass

    def test_get_guacamole_config(self):
        pass


class TestHackathonNotifyApi(ApiTestCase):
    def test_list_notifies(self):
        pass


class TestGrantedAwards(ApiTestCase):
    def test_get_granted_awards(self):
        pass

    def test_get_hackathon_granted_awards(self):
        pass
