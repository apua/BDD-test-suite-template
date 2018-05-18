from robot.api import logger
import requests

requests.packages.urllib3.disable_warnings()


class Client:
    """
    A stateful agent for REST API
    """
    def __init__(self, root_url):
        self.root_url = root_url
        self.session = requests.Session()
        self.session.verify = False
        self.session.trust_env = False
        self.user_name = None
        self.token = None

    def post(self, location, json_data):
        logger.debug('payload -> {json_data}'.format(**locals()))
        return self.session.post(self.root_url + location, json=json_data)

    def get(self, location):
        return self.session.get(self.root_url + location)

    def put(self, location, json_data):
        logger.debug('payload -> {json_data}'.format(**locals()))
        return self.session.put(self.root_url + location, json=json_data)

    def delete(self, location):
        return self.session.delete(self.root_url + location)
