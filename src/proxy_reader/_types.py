from typing import TypedDict, NotRequired, List, Iterator, TypeAlias
from .proxy import Proxy


class TelegramHTTP(TypedDict):
    proxy_type: int
    addr: str
    port: int
    username: NotRequired[str]
    password: NotRequired[str]


ProxiesList: TypeAlias = List[Proxy]
ProxyiesGen: TypeAlias = Iterator[Proxy]
