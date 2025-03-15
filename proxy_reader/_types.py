from typing import TypedDict, NotRequired, List, Iterator, TypeAlias, Any, Optional
from .proxy import Proxy


class TelegramHTTP(TypedDict):
    proxy_type: int
    addr: str
    port: int
    username: NotRequired[str]
    password: NotRequired[str]


GeneralDict: TypeAlias = dict[str, Any]

ProxiesList: TypeAlias = List[Proxy]
ProxyiesGen: TypeAlias = Iterator[Proxy]


class ProxyDictT(TypedDict):
    host: str
    port: str
    username: Optional[str]
    password: Optional[str]
