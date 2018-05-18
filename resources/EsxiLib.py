from pysphere import VIServer

def get_ipv4_addresses(vm, from_cache=False):
    import re
    ipv4_address_form = re.compile(r'\d+\.\d+\.\d+\.\d+')
    net = vm.get_property('net', from_cache=from_cache)
    if net is not None:
        for nic in net:
            for ip in nic['ip_addresses']:
                if ipv4_address_form.match(ip):
                        yield ip

class EsxiLib(object):
    def __init__(self, ip, username, password, **kwargs):
        self.ip = ip
        self.username = username
        self.password = password
        self.kwargs = kwargs
        self.connect()

    def __del__(self):
        if not hasattr(self, 'server') and self.server.is_connected():
            self.server.disconnect()

    def connect(self):
        if not hasattr(self, 'server'):
            self.server = VIServer()
        self.server.connect(self.ip, self.username, self.password)

    def get_vm_by_name(self, name):
        return self.server.get_vm_by_name(name)

    def get_ip(self, vmname):
        import time
        timeout = 60 * 5 # min
        period = 5
        vm=self.get_vm_by_name(vmname)
        for t in range(timeout//period):
            ips = tuple(get_ipv4_addresses(vm, from_cache=False))
            if ips:
                return ips[0]
            time.sleep(period)
        else:
            raise Exception("cannot get VM IP in %s seconds" % timeout)
