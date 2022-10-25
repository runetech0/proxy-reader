

class Proxy:
    def __init__(self, ip=None, port=None, username=None, password=None):
        self._ip = ip
        self._port = port
        self._username = username
        self._password = password

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def http(self):
        if self.username is not None and self.password is not None:
            return f'http://{self._username}:{self._password}@{self._ip}:{self._port}'
        return f'http://{self._ip}:{self._port}'

    @property
    def https(self):
        if self.username is not None and self.password is not None:
            return f'https://{self._username}:{self._password}@{self._ip}:{self._port}'
        return f'https://{self._ip}:{self._port}'

    @property
    def telegram_http(self):
        p = {
            "proxy_type": 3,
            "addr": self._ip,
            "port": int(self._port)
        }
        if self.username is not None and self.password is not None:
            p.update({
                "username": self.username,
                "password": self.password
            })
        return p

    @property
    def telegram_socks5(self):
        p = {
            "proxy_type": 2,
            "addr": self._ip,
            "port": int(self._port)
        }
        if self.username is not None and self.password is not None:
            p.update({
                "username": self.username,
                "password": self.password
            })
        return p

    @property
    def telegram_socks4(self):
        p = {
            "proxy_type": 1,
            "addr": self._ip,
            "port": int(self._port)
        }
        if self.username is not None and self.password is not None:
            p.update({
                "username": self.username,
                "password": self.password
            })
        return p

    @property
    def socks5(self):
        if self._username is not None and self._password is not None:
            return f"socks5://{self._username}:{self._password}@{self.ip}:{self.port}"
        return f"socks5://{self.ip}:{self.port}"

    @property
    def socks4(self):
        if self._username is not None and self._password is not None:
            return f"socks4://{self._username}:{self._password}@{self.ip}:{self.port}"
        return f"socks4://{self.ip}:{self.port}"

    def __repr__(self):
        if self._username is not None and self._password is not None:
            return f'{self._ip}:{self._port}:{self._username}:{self._password}'
        return f'{self._ip}:{self._port}'
