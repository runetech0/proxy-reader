import random
import itertools
import urllib.request
import typing
import traceback


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
            self._proxies: typing.List[Proxy] = self._read_auth_proxies()
        else:
            self._proxies: typing.List[Proxy] = self._read_proxies()
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

    def _is_working(self, http=None, https=None):
        try:
            proxy_handler = urllib.request.ProxyHandler(
                {'https': https, "http": http})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            # change the url address here
            urllib.request.urlopen('https://www.myip.com/')
        except urllib.error.HTTPError as e:
            return False
        except Exception:
            # traceback.print_exc()
            return False
        return True

    def get_proxy(self, check=True, debug=False):
        for proxy in itertools.cycle(self._proxies):
            if check:
                http = proxy.http_with_auth if self._has_auth else proxy.http
                https = proxy.https_with_auth if self._has_auth else proxy.https
                if not self._is_working(http=http, https=https):
                    if debug:
                        print(f'{http} not working')
                    continue
            if debug:
                print(f'{http} is working')
            yield proxy

    def validate_all_http(self):
        validated = list()
        for proxy in self._proxies:
            http = proxy.http
            if self._has_auth:
                http = proxy.http_with_auth if self._has_auth else proxy.http
                https = proxy.https_with_auth if self._has_auth else proxy.https
            print(f"Checking {http}")
            if self._is_working(http=http, https=https):
                validated.append(proxy)
        self._proxies = validated.copy()
        print(f"Total valid proxies : {len(self._proxies)}")
