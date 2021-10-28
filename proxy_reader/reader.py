import random
import itertools
import socks


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

    @property
    def telegram_http(self):
        return {
            "proxy_type": 3,
            "addr": self._ip,
            "port": int(self._port)
        }

    @property
    def telegram_http_auth(self):
        return {
            "proxy_type": 3,
            "addr": self._ip,
            "port": int(self._port),
            "username": self._username,
            "password": self._password
        }

    @property
    def telegram_socks5(self):
        return {
            "proxy_type": 2,
            "addr": self._ip,
            "port": int(self._port)
        }

    @property
    def telegram_socks5_auth(self):
        return {
            "proxy_type": 2,
            "addr": self._ip,
            "port": int(self._port),
            "username": self._username,
            "password": self._password
        }

    def __repr__(self):
        return f'{self._ip}:{self._port}'


class ReadProxies:
    def __init__(self, file_path="./proxies.txt", fields_separator=",", has_auth=False,
                 proxy_index=0, username_index=1,
                 password_index=2, shuffle=False):
        self._file_path = file_path
        if fields_separator == ":":
            raise ValueError("fields_separator cannot be colon (:) ")
        self._fields_separator = fields_separator
        self._has_auth = has_auth
        self._proxy_index = proxy_index
        self._username_index = username_index
        self._password_index = password_index
        if self._has_auth:
            self._proxies = self._read_auth_proxies()
        else:
            self._proxies = self._read_proxies()
        if shuffle:
            random.shuffle(self._proxies)

    def _read_auth_proxies(self):
        with open(self._file_path, 'r') as f:
            raw = f.read().splitlines()
        proxies = list()
        for proxy in raw:
            details = proxy.split(self._fields_separator)
            ip, port = details[self._proxy_index].split(":")
            proxies.append(Proxy(
                ip=ip, port=port, username=details[self._username_index], password=details[self._password_index]))
        return proxies

    def _read_proxies(self):
        with open(self._file_path, 'r') as f:
            raw = f.read().splitlines()
        proxies = list()
        for proxy in raw:
            details = proxy.split(self._fields_separator)
            ip, port = details[self._proxy_index].split(":")
            proxies.append(Proxy(ip, port))
        return proxies

    @property
    def total(self):
        return len(self._proxies)

    def __repr__(self):
        return str(self._proxies)

    def get_proxy(self):
        for proxy in itertools.cycle(self._proxies):
            yield proxy
