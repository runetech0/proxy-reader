import aiofiles

from .models.proxy import Proxy
from .utils import parse_proxy_line


class ProxiesReader:
    def __init__(self, list_of_proxies: list[str]) -> None:
        self._proxies: list[Proxy] = [
            Proxy(parse_proxy_line(p)) for p in list_of_proxies
        ]

    @property
    def proxies(self) -> list[Proxy]:
        return self._proxies

    @classmethod
    async def read_proxies_from_file(cls, file_path: str) -> "ProxiesReader":
        proxies: list[str] = []
        async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
            async for line in file:
                proxies.append(line.strip())

        return cls(list(set(proxies)))
