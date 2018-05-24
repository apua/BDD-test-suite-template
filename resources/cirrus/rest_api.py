class StatefulClient:
    def __init__(self, root_url):
        import requests
        requests.packages.urllib3.disable_warnings()

        self.session = requests.Session()
        self.session.verify = False
        self.session.trust_env = False

        self.root_url = root_url
        self.user_name = None

    def _method(self, meth, path, json_data=None):
        from urllib.parse import urljoin
        uri = urljoin(self.root_url, path)
        if json_data is None:
            print('*DEBUG* payload -> {json_data}'.format(**locals()))
        return getattr(self.session, meth)(uri, json=json_data)

    def _get(self, path):
        return self._method('get', path)

    def _post(self, path, json_data):
        return self._method('post', path, json_data)

    def _put(self, path, json_data):
        return self._method('put', path, json_data)

    def _delete(self, path):
        return self._method('delete', path)


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


def auto_login(cls):
    import ast, inspect, textwrap
    cls_source = inspect.getsource(cls)
    tree = ast.parse(cls_source)
    class_def = tree.body[0]
    for stmt in class_def.body:
        if isinstance(stmt, ast.FunctionDef):
            assert 'credential' not in getattr(cls, stmt.name).__code__.co_varnames, stmt.name
            self_var = stmt.args.args[0].arg
            ref = ast.parse(textwrap.dedent(f'''\
                    def ref({self_var}, credential=None):
                        if credential:
                            if {self_var}.user_name is None:
                                {self_var}.login(**credential)
                            elif credential['user_name'] != {self_var}.user_name:
                                {self_var}.logout()
                                {self_var}.login(**credential)
                            else:
                                pass
                    ''')).body[0]
            stmt.args.args.append(ref.args.args[-1])
            stmt.args.defaults.append(ref.args.defaults[-1])
            stmt.body = ref.body + stmt.body
    exec(compile(tree, '<string>', 'exec'))
    return locals()[cls.__name__]


@auto_login
class CirrusApi:
    def add_hardware(self, hw):
        return 1

    def create_reservation(self, rsv):
        return 2

    def release_reservation(self, rsv_id):
        pass

    def detail_reservation(self, rsv_id):
        if rsv_id == 3:
            raise AssertionError('HTTP 404 NOT FOUND')
        return 'reservation data'


class RestApi(CirrusApi, AtlasApi, StatefulClient):
    """
    REST API keywords
    """
