import uuid
import json
import logging
from datetime import timedelta, datetime

from hackathon import app
from hackathon.hmongo.models import UserToken
from hackathon.hmongo.database import drop_db, setup_db

DEFAULT_TEST_CLIENT_HEADERS = {
    'User-Agent': "OH/TestClient",
    'Accept-Encoding': ', '.join(('gzip', 'deflate')),
    'Accept': '*/*',
    "Content-Type": "application/json",
    'Connection': 'keep-alive',
}


class ApiTestError(Exception):
    pass


class ApiStatusCodeError(ApiTestError):
    def __init__(self, expect_sc, crt_sc):
        self.expect_status_code = expect_sc
        self.current_status_code = crt_sc

    def __str__(self):
        return "Expect to get status code {}, but currently get {}" \
            .format(self.expect_status_code, self.current_status_code)


class ApiJsonLoadError(ApiTestError):
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return "Load response to json error, get content: {}".format(self.content)


class TestClient(object):

    def __init__(self):
        self._app = app
        self._client = app.test_client()
        self._headers = DEFAULT_TEST_CLIENT_HEADERS
        self.log = logging.getLogger("test_client")

    def result(self, resp, is_json):
        text = resp.data.decode()
        self.log.info("get response content: {}".format(text))
        if is_json:
            return json.loads(text)
        return text

    def get(self, url, status_code=200, is_json=True, **kwargs):
        with self._app.app_context():
            resp = self._client.get(url, headers=self._headers, **kwargs)
        if resp.status_code != status_code:
            raise ApiStatusCodeError(status_code, resp.status_code)
        return self.result(resp, is_json)

    def post(self, url, json_data=None, status_code=200, is_json=True, **kwargs):
        data = json.dumps(json_data)
        with self._app.app_context():
            resp = self._client.post(url, headers=self._headers, data=data, **kwargs)
        if resp.status_code != status_code:
            raise ApiStatusCodeError(status_code, resp.status_code)
        return self.result(resp, is_json)

    def put(self, url, json_data=None, status_code=200, is_json=True, **kwargs):
        data = json.dumps(json_data)
        with self._app.app_context():
            resp = self._client.put(url, headers=self._headers, data=data, **kwargs)
        if resp.status_code != status_code:
            raise ApiStatusCodeError(status_code, resp.status_code)
        return self.result(resp, is_json)

    def patch(self, url, json_data=None, status_code=200, is_json=True, **kwargs):
        data = json.dumps(json_data)
        with self._app.app_context():
            resp = self._client.patch(url, headers=self._headers, data=data, **kwargs)
        if resp.status_code != status_code:
            raise ApiStatusCodeError(status_code, resp.status_code)
        return self.result(resp, is_json)

    def delete(self, url, json_data=None, status_code=200, is_json=True, **kwargs):
        data = json.dumps(json_data)
        with self._app.app_context():
            resp = self._client.delete(url, headers=self._headers, data=data, **kwargs)
        if resp.status_code != status_code:
            raise ApiStatusCodeError(status_code, resp.status_code)
        return self.result(resp, is_json)

    def update_headers(self, headers):
        self._headers.update(headers)


class ApiTestCase(object):
    client = TestClient()
    log = logging.getLogger("api_test")

    def login(self, user):
        token_issue_date = datetime.utcnow()
        valid_period = timedelta(minutes=1)
        token_expire_date = token_issue_date + valid_period
        user_token = UserToken(token=str(uuid.uuid1()),
                               user=user,
                               expire_date=token_expire_date,
                               issue_date=token_issue_date)
        user_token.save()
        self.client.update_headers(dict(token=user_token.token))
        return user_token

    @classmethod
    def setup_class(cls):
        cls.log.info("init database")
        drop_db()
        setup_db()

    @classmethod
    def teardown_class(cls):
        cls.log.info("clean database")
        drop_db()
