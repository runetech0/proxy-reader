from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, Any


if TYPE_CHECKING:
    from ._types import GeneralDict, ProxyDictT


class Proxy:
    def __init__(
        self,
        proxy: ProxyDictT,
    ) -> None:
        self._proxy = proxy

    @property
    def ip(self) -> str:
        return self._proxy["host"]

    @property
    def port(self) -> str:
        return self._proxy["port"]

    @property
    def username(self) -> Optional[str]:
        return self._proxy["username"]

    @property
    def password(self) -> Optional[str]:
        return self._proxy["password"]

    @property
    def http(self) -> str:
        if self.username and self.password:
            return f"http://{self.username}:{self.password}@{self.ip}:{self.port}"
        return f"http://{self.ip}:{self.port}"

    @property
    def https(self) -> str:
        if self.username and self.password:
            return f"https://{self.username}:{self.password}@{self.ip}:{self.port}"
        return f"https://{self.ip}:{self.port}"

    @property
    def telegram_http(self) -> Dict[str, Any]:
        p: GeneralDict = {"proxy_type": 3, "addr": self.ip, "port": int(self.port)}
        if self.username and self.password:
            p.update({"username": self.username, "password": self.password})
        return p

    @property
    def telegram_socks5(self) -> Dict[str, Any]:
        p: GeneralDict = {"proxy_type": 2, "addr": self.ip, "port": int(self.port)}
        if self.username and self.password:
            p.update({"username": self.username, "password": self.password})
        return p

    @property
    def telegram_socks4(self) -> Dict[str, Any]:
        p: GeneralDict = {"proxy_type": 1, "addr": self.ip, "port": int(self.port)}
        if self.username and self.password:
            p.update({"username": self.username, "password": self.password})
        return p

    @property
    def socks5(self) -> str:
        if self.username is not None and self.password is not None:
            return f"socks5://{self.username}:{self.password}@{self.ip}:{self.port}"
        return f"socks5://{self.ip}:{self.port}"

    @property
    def socks4(self) -> str:
        if self.username is not None and self.password is not None:
            return f"socks4://{self.username}:{self.password}@{self.ip}:{self.port}"
        return f"socks4://{self.ip}:{self.port}"

    def __str__(self) -> str:
        if self.username is not None and self.password is not None:
            return f"{self.ip}:{self.port}:{self.username}:{self.password}"
        return f"{self.ip}:{self.port}"

    def __repr__(self) -> str:
        return self.__str__()
