from typing import Optional, Dict, Any


class Proxy:
    def __init__(self, ip: str, port: str, username: Optional[str] = None, password: Optional[str] = None) -> None:
        self._ip = ip
        self._port = port
        self._username = username
        self._password = password

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> str:
        return self._port

    @property
    def username(self) -> Optional[str]:
        return self._username

    @property
    def password(self) -> Optional[str]:
        return self._password

    @property
    def http(self) -> str:
        if self.username and self.password:
            return f"http://{self._username}:{self._password}@{self._ip}:{self._port}"
        return f"http://{self._ip}:{self._port}"

    @property
    def https(self) -> str:
        if self.username and self.password:
            return f"https://{self._username}:{self._password}@{self._ip}:{self._port}"
        return f"https://{self._ip}:{self._port}"

    @property
    def telegram_http(self) -> Dict[str, Any]:
        p = {"proxy_type": 3, "addr": self._ip, "port": int(self._port)}
        if self.username and self.password:
            p.update({"username": self.username, "password": self.password})
        return p

    @property
    def telegram_socks5(self) -> Dict[str, Any]:
        p = {"proxy_type": 2, "addr": self._ip, "port": int(self._port)}
        if self.username and self.password:
            p.update({"username": self.username, "password": self.password})
        return p

    @property
    def telegram_socks4(self) -> Dict[str, Any]:
        p = {"proxy_type": 1, "addr": self._ip, "port": int(self._port)}
        if self.username and self.password:
            p.update({"username": self.username, "password": self.password})
        return p

    @property
    def socks5(self) -> str:
        if self._username is not None and self._password is not None:
            return f"socks5://{self._username}:{self._password}@{self.ip}:{self.port}"
        return f"socks5://{self.ip}:{self.port}"

    @property
    def socks4(self) -> str:
        if self._username is not None and self._password is not None:
            return f"socks4://{self._username}:{self._password}@{self.ip}:{self.port}"
        return f"socks4://{self.ip}:{self.port}"

    def __str__(self) -> str:
        if self._username is not None and self._password is not None:
            return f"{self._ip}:{self._port}:{self._username}:{self._password}"
        return f"{self._ip}:{self._port}"

    def __repr__(self) -> str:
        return self.__str__()
