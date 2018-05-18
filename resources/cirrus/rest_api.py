from robot.api import logger

from .client import Client
from .utils import to_timedelta, ceil, parse_isoformat, to_isoformat


def support_create_session(method):
    from functools import wraps

    # NOTE: in Python3.x, write below for more readable
    #       `def method_(self, *a, credential=None, **kw): ...`
    @wraps(method)
    def method_(self, *a, **kw):
        try:
            credential = kw.pop('credential')
        except KeyError:
            credential = None

        if credential is None:
            return method(self, *a, **kw)
        else:
            logger.debug('create session for {credential}'.format(**locals()))

            api = type(self)(self.client.root_url)
            api.login(**credential)
            self = api
            try:
                return method(self, *a, **kw)
            finally:
                api.logout()

    return method_


class RestAPI:
    def __init__(self, root_url):
        self.client = Client(root_url)

    def login(self, user_name, password):
        resp = self.client.post('/rest/login-sessions', {
            'userName': user_name,
            'password': password,
            })
        assert resp.status_code == 200, resp.json()
        self.client.user_name = user_name
        self.client.token = resp.json()['sessionID']
        self.client.session.headers.update({'auth': self.client.token})

    def logout(self):
        resp = self.client.delete('/rest/login-sessions')
        assert resp.status_code == 204, resp.json()
        self.client.user_name = None
        self.client.token = None
        del self.client.session.headers['auth']

    #@support_create_session
    #def add_hardware(self, hw):
    #    """
    #    :type hw: namedtuple('Hardware', ('id', 'name', 'desc', 'type'))
    #    """
    #    # NOTE: support "Generic" type only currently
    #    payload = [{
    #            'inventory_interval': '0',
    #            'inventory_limit': 'no inventory',
    #            'inventory_override': 'false',
    #            'inventory_type': 'Global',
    #            'pause_inventory': 'false',
    #            'owner_type': 'users',
    #            'owner': self.client.user_name,
    #            'name': hw.name,
    #            'desc': hw.desc,
    #            'type': hw.type,
    #            }]
    #    resp = self.client.post('/rest/cirrus/servers', payload)
    #    assert resp.status_code == 200, resp.text
    #    hw_id = int(resp.json()['hardwareData'][0]['id'])
    #    return hw_id

    #@support_create_session
    #def reserve_hardware(self, hw_id, start_dt, duration):
    #    """
    #    :type duration: [str | float | timedelta]
    #    :return: reservation id
    #    :rtype: int
    #    """
    #    duration = to_timedelta(duration)
    #    end_dt = start_dt + duration
    #    payload = {
    #        'desc': '',
    #        'rrule': '',
    #        'start_time': to_isoformat(start_dt),
    #        'end_time': to_isoformat(end_dt),
    #        'hw_id': int(hw_id),
    #        }
    #    resp = self.client.post('/rest/cirrus/reservation', payload)
    #    assert resp.status_code == 201, resp.text
    #    return int(resp.json()['uri'].rsplit('/', 1)[-1])

    #@support_create_session
    #def query_index_resource(self, category, query):
    #    resp = self.client.get('/rest/index/resources?category={category}&query={query}'.format(**locals()))
    #    assert 'members' in resp.json(), resp.json()
    #    return resp.json()['members']

    #@support_create_session
    #def release_reservation(self, rsv_id):
    #    resp = self.client.delete('/rest/cirrus/reservation/{rsv_id}'.format(**locals()))
    #    assert resp.status_code == 204, resp.text

    #@support_create_session
    #def detail_reservation(self, rsv_id):
    #    """
    #    Example of reservation response::

    #        {
    #            'start_time': '2018-05-09T14:30:00.000000Z',
    #            'end_time': '2018-05-09T15:00:00.000000Z',
    #            'owner': 'administrator',
    #            'desc': '',
    #            'hw_id': 346,
    #            'rrule': ''
    #            }

    #    :rtype: namedtuple('Reservation', ('id', 'hw_id', 'start', 'end', 'desc', 'rrule'))
    #    """
    #    import collections

    #    resp = self.client.get('/rest/cirrus/reservation/{rsv_id}'.format(**locals()))
    #    assert resp.status_code == 200, resp.text

    #    Reservation = collections.namedtuple('Reservation', ('id', 'hw_id', 'start', 'end', 'desc', 'rrule'))
    #    rsv = resp.json()
    #    assert isinstance(rsv['hw_id'], int), rsv
    #    return Reservation(
    #            id=rsv_id,
    #            hw_id=rsv['hw_id'],
    #            start=parse_isoformat(rsv['start_time']),
    #            end=parse_isoformat(rsv['end_time']),
    #            desc=rsv['desc'],
    #            rrule=rsv['rrule'],
    #            )

    #@support_create_session
    #def update_reservation(self, rsv):
    #    """
    #    :type rsv: namedtuple('Reservation', ('id', 'hw_id', 'start', 'end', 'desc', 'rrule'))
    #    """
    #    update_info = {
    #            'desc': rsv.desc,
    #            'hw_id': rsv.hw_id,
    #            'rrule': rsv.rrule,
    #            'start_time': to_isoformat(rsv.start),
    #            'end_time': to_isoformat(rsv.end),
    #            }
    #    resp = self.client.put('/rest/cirrus/reservation/{rsv.id}'.format(**locals()), update_info)
    #    assert resp.status_code == 200, resp.text

    #def execute_test_plan(self, test_plan):
    #    test_plan_api_location = '/rest/cirrus/jobs'
    #    test_plan['info']['login_name'] = str(self.client.user_name)
    #    return self.client.post(test_plan_api_location, test_plan)



from . import models

class MockAPI(RestAPI):
    def __init__(self, root_url):
        self.client = Client(root_url)
    
    @support_create_session
    def query_index_resource(self, category, query):
        return []

    @support_create_session
    def add_hardware(self, hw=None):
        return 1

    @support_create_session
    def create_reservation(self, rsv):
        return 2

    @support_create_session
    def detail_reservation(self, rsv_id):
        return models.Reservation(2, 1, 3, 4, '5', '6')

    @support_create_session
    def update_reservation(self, rsv):
        ...

    @support_create_session
    def release_reservation(self, rsv_id):
        ...

RestAPI = MockAPI
