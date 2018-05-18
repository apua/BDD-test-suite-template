# NOTE: for TAE development only

import sys
from contextlib import contextmanager

from .rest_api import RestAPI
from .client import Client
from .keywords import *


if len(sys.argv) != 4:
    exit("usage: python -m cirrus $appliance_ip $user_name $password")


# test connection via EULA API
client = Client('https://' + sys.argv[1])

resp = client.get('/rest/appliance/eula/status')
assert resp.status_code == 200, resp.json()


# test API via login/logout method
api = RestAPI(sys.argv[1])
api.login(sys.argv[2], sys.argv[3])
api.logout()


# provide REST API context manager for below tests
@contextmanager
def rest_api(appliance_ip, user_name, password):
    api = RestAPI(appliance_ip)
    api.login(user_name, password)
    try:
        yield api
    finally:
        api.logout()


with rest_api(*sys.argv[1:]) as api:
    "write unit test here"
