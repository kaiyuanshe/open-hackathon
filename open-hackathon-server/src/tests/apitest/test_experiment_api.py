from . import ApiTestCase


class TestUserExperiment(ApiTestCase):

    def test_start_experiment(self, user1):
        self.client.post("/api/user/experiment")

    def test_stop_experiment(self, user1):
        self.client.delete("/api/user/experiment")

    def test_get_experiment(self, user1):
        self.client.get("/api/user/experiment")

    def test_experiment_heart_beat(self, user1):
        self.client.put("/api/user/experiment")
