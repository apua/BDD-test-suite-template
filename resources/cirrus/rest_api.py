from urllib.parse import urljoin

import requests
from robot.api import logger


requests.packages.urllib3.disable_warnings()


class StatefulClient:
    def __init__(self, root_url):
        self.session = requests.Session()
        self.session.verify = False
        self.session.trust_env = False

        self.root_url = root_url
        self.user_name = None

    def _get(self, path):
        uri = urljoin(self.root_url, path)
        return self.session.get(uri)

    def _post(self, path, json_data):
        logger.debug('payload -> {json_data}'.format(**locals()))
        uri = urljoin(self.root_url, path)
        return self.session.post(uri, json=json_data)

    def _put(self, path, json_data):
        logger.debug('payload -> {json_data}'.format(**locals()))
        uri = urljoin(self.root_url, path)
        return self.session.put(uri, json=json_data)

    def _delete(self, path):
        uri = urljoin(self.root_url, path)
        return self.session.delete(uri)


# NOTE: unknown Atlas version so far
class AtlasApi:
    def login(self, user_name, password):
        resp = self._post('/rest/login-sessions', {
            'userName': user_name,
            'password': password,
            })
        if not resp.status_code == 200:
            raise AssertionError(resp.json())
        self.user_name = user_name
        self.session.headers.update({'auth': resp.json()['sessionID']})

    def logout(self):
        resp = self._delete('/rest/login-sessions')
        if not resp.status_code == 204:
            raise AssertionError(resp.json())
        self.user_name = None
        del self.session.headers['auth']

    def logout_if_any(self):
        if 'auth' in self.session.headers:
            self.logout()


class CirrusApi:
    def add_hardware(self, hw, credential=None):
        return 1

    def create_reservation(self, rsv, credential=None):
        return 2

    def release_reservation(self, rsv_id, credential=None):
        pass

    def detail_reservation(self, rsv_id, credential=None):
        if rsv_id == 3:
            raise AssertionError('HTTP 404 NOT FOUND')
        return 'reservation data'


class RestApi(CirrusApi, AtlasApi, StatefulClient):
    """
    REST API keywords
    """
