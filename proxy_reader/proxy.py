

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
