from . import ApiTestCase


class TestTeamApi(ApiTestCase):

    def test_create_team(self):
        # not found 
        data = {
            'id':'1',
        }
        payload = self.client.post('/api/team', json_data=data)
        assert payload['code'] == 200

    def test_update_team(self):
        # ok
        data = {
            'id':'1',
        }
        payload = self.client.put('/api/team', json_data=data)
        assert payload['code'] == 200

    def test_delete_team(self):
        data = {
            'id':'1',
        }
        payload = self.client.delete('/api/team', json_data=data)
        assert payload['code'] == 200

    def test_dismiss_team(self):
        # not found
        pass

    def test_query_team(self):
        # not found
        pass

    def test_list_team_in_hackathon(self):
        # not found 
        data =  "id=1&name=test&number=1"
        payload = self.client.get('/api/hackathon/team/list?{}'.format(data))
        assert payload['code'] == 200
        

    def test_get_team_score(self):
        data = "pattern=test"
        payload = self.client.get('/api/admin/team/score/list?{}'.format(data))
        assert payload['code'] == 200


    def test_get_team_info(self):
        data = 'id=1'

        payload = self.client.get('/api/team?{}'.format(data))
        assert payload['code'] == 200

    def test_get_team_templates(self):
        


class TestTeamMemberApi(ApiTestCase):
    def test_get_user_team(self):
        pass

    def test_get_team_member(self):
        data = "id=1"
        payload = self.client.get('/api/team/member/list?{}'.format(data))
        assert payload['code'] == 200
