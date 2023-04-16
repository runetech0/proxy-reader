from typing import Any, Dict, Optional

class Proxy:
    def __init__(self, ip: str, port: str, username: Optional[str] = ..., password: Optional[str] = ...) -> None: ...
    @property
    def ip(self) -> str: ...
    @property
    def port(self) -> str: ...
    @property
    def username(self) -> Optional[str]: ...
    @property
    def password(self) -> Optional[str]: ...
    @property
    def http(self) -> str: ...
    @property
    def https(self) -> str: ...
    @property
    def telegram_http(self) -> Dict[str, Any]: ...
    @property
    def telegram_socks5(self) -> Dict[str, Any]: ...
    @property
    def telegram_socks4(self) -> Dict[str, Any]: ...
    @property
    def socks5(self) -> str: ...
    @property
    def socks4(self) -> str: ...
