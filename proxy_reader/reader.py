import random
import itertools
import urllib.request
import typing
import threading


class Proxy:
    def __init__(self, ip=None, port=None, username=None, password=None):
        self._ip = ip
        self._port = port
        self._username = username
        self._password = password

    @property
    def ip(self):
        return self._ip

    @ip.getter
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @port.getter
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @username.getter
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @password.getter
    def password(self):
        return self._password

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

        self._working_proxies = list()
        self._non_working_proxies = list()

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

    def _is_working(self, http=None, https=None, full_proxy=None, log=False):
        try:
            proxy_handler = urllib.request.ProxyHandler(
                {'https': https, "http": http})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            # change the url address here
            urllib.request.urlopen('https://www.example.com')

            if full_proxy:
                self._working_proxies.append(full_proxy)

            if log:
                print(f"{full_proxy} : WORKING")

            return True

        except (urllib.error.HTTPError, Exception):
            if full_proxy:
                self._non_working_proxies.append(full_proxy)

            if log:
                print(f"{full_proxy} : NOT-WORKING")

            return False

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
                print(f'{proxy} is working')
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

    def get_all_working_proxies(self, log=False) -> typing.List[Proxy]:
        threads = list()
        for proxy in self._proxies:

            # print(f"Checking proxy {proxy}")
            http = proxy.http_with_auth if self._has_auth else proxy.http
            https = proxy.https_with_auth if self._has_auth else proxy.https

            t = threading.Thread(target=self._is_working, kwargs={
                "http": http, "https": https, "full_proxy": proxy, "log": True})

            t.start()
            threads.append(t)

        for i, t in enumerate(threads):
            t.join()

        if log:
            print("Done checking all proxies")

        return self._working_proxies
