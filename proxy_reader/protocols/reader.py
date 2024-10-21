from typing import List, Optional, Dict, Any, Protocol
from .._types import ProxiesList
from ..proxy import Proxy


class ProxiesReaderProtocol(Protocol):
    @property
    def total(self) -> int:
        pass

    @property
    def total_working(self) -> int:
        pass

    @property
    def total_bad(self) -> int:
        pass

    @property
    def proxies(self) -> ProxiesList:
        pass

    @property
    def bad_proxies(self) -> ProxiesList:
        pass

    @property
    def working_proxies(self) -> ProxiesList:
        pass

    @working_proxies.setter
    def working_proxies(self, working_proxies: List[Proxy]) -> None:
        pass

    def read_raw(self) -> List[str]:
        pass

    def random_url(self) -> str:
        pass

    def read_with_auth(self) -> None:
        pass

    def read_authless(self) -> None:
        pass

    async def _check_proxy(
        self, proxy: Proxy, response_time: Optional[int] = None
    ) -> bool:
        pass

    async def check_all_proxies(self, max_resp_time: int = 30) -> None:
        pass

    async def _check_proxy_socks(
        self, proxy: Proxy, response_time: Optional[int] = None
    ) -> bool:
        pass

    async def check_all_proxies_socks5(self, max_resp_time: int = 5) -> None:
        pass

    def get_working_proxies_list_http(self) -> List[str]:
        pass

    def write_working_proxies(self, filename: str) -> None:
        pass

    def get_random_http(self) -> Optional[str]:
        pass

    def get_random_socks5(self) -> Optional[str]:
        pass

    def get_random_socks5_telegram(self) -> Optional[Dict[str, Any]]:
        pass

    def next_http_from_list(self) -> Optional[str]:
        pass

    def next_http_from_cycle(self) -> str:
        pass

    def next_socks5_from_list(self) -> str:
        pass

    def next_socks5_from_cycle(self) -> str:
        pass

    def next_http_telegram_from_list(self) -> Dict[str, Any]:
        pass

    def next_http_telegram_from_cycle(self) -> Dict[str, Any]:
        pass

    def next_socks5_telegram_from_cycle(self) -> Dict[str, Any]:
        pass

    def next_socks5_telegram_from_list(self) -> Dict[str, Any]:
        pass

    def next_https_from_list(self) -> str:
        pass

    def next_https_from_cycle(self) -> str:
        pass
