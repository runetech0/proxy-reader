import random
import itertools

class Proxy:
    def __init__(self, ip=None, port=None, username=None, password=None):
        self._ip = ip
        self._port = port
        self._username = username
        self._password = password 

    @property
    def http(self):
        return f'http://{self._ip}:{self._port}'

    @property
    def https(self):
        return f'https://{self._ip}:{self._port}'

    @property
    def http_with_auth(self):
        return f'http://{self._username}:{self._password}@{self._ip}:{self._port}'

    @property
    def https_with_auth(self):
        return f'https://{self._username}:{self._password}@{self._ip}:{self._port}'


    def __repr__(self):
        return f'{self._ip}:{self._port}'

class ReadProxies:
    def __init__(self, file_path="./proxies.txt", fields_separator=",", has_auth=False, proxy_index=0, username_index=1, password_index=2):
        self._file_path = file_path
        self._fields_separator = fields_separator
        self._has_auth = has_auth
        self._proxy_index = proxy_index
        self._username_index = username_index
        self._password_index = password_index
        if self._has_auth:
            self._proxies = self._read_auth_proxies()
        else:
            self._proxies = self._read_proxies()

    def _read_auth_proxies(self):
        raw = open(self._file_path).read().splitlines()
        proxies = list()
        for proxy in raw:
            details = proxy.split(self._fields_separator)
            ip, port = details[self._proxy_index].split(":")
            proxies.append(Proxy(ip, port, details[self._username_index], details[self._password_index]))
        random.shuffle(proxies)
        return proxies


    def _read_proxies(self):
        raw = open("proxies.txt").read().splitlines()
        proxies = list()
        for proxy in raw:
            details = proxy.split(self._fields_separator)
            ip, port = details[self._proxy_index].split(":")
            proxies.append(Proxy(ip, port))
        random.shuffle(proxies)
        return proxies

    @property
    def total(self):
        return len(self._proxies)


    def __repr__(self):
        return str(self._proxies)

    def get_proxy(self):
        for proxy in itertools.cycle(self._proxies):
            yield proxy
