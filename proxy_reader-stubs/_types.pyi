from .proxy import Proxy as Proxy
from typing import NotRequired, TypeAlias, TypedDict

class TelegramHTTP(TypedDict):
    proxy_type: int
    addr: str
    port: int
    username: NotRequired[str]
    password: NotRequired[str]

ProxiesList: TypeAlias
ProxyiesGen: TypeAlias
