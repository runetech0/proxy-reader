import random
import itertools
from .proxy import Proxy
import aiohttp
import asyncio
from .logger import logger, console_handler, file_handler
import os
from aiohttp_socks import ProxyConnector  # pyright: ignore[reportMissingTypeStubs]
import sys
from typing import Optional, List, Dict, Any
from ._types import ProxiesList, ProxyiesGen


class ProxiesReader:
    def __init__(
        self, file_path: str = "./proxies.txt", shuffle: bool = False, debug: bool = False, extra_debug: bool = False
    ) -> None:
        self._file_path = file_path
        self._debug = debug
        self._extra_debug = extra_debug

        self._shuffle = shuffle
        self._proxies: ProxiesList = []
        self._has_auth = False
        self._bad_proxies: ProxiesList = []
        self._working_proxies: ProxiesList = []
        self._proxies_checked = False
        self._proxy_iterator: Optional[ProxyiesGen] = None
        self._proxy_iterator_cycle: Optional[ProxyiesGen] = None
        self._thread_control: asyncio.Semaphore = asyncio.Semaphore(500)
        self._max_response_time = 60
        self._timeout_count = 0

        self._check_urls = [
            "https://duckduckgo.com/manifest.json",
            "https://duckduckgo.com/favicon.ico",
            "https://duckduckgo.com/ti6.js",
            "https://duckduckgo.com/locale/en_US/duckduckgo14.js",
            "https://duckduckgo.com/lib/l132.js",
            "https://duckduckgo.com/b203.js",
            "https://duckduckgo.com/tl7.js",
            "https://duckduckgo.com/post3.html",
            # "https://www.cloudflare.com/cdn-cgi/trace",
        ]

        if not self._debug:
            logger.removeHandler(file_handler)
            logger.removeHandler(console_handler)
            try:
                os.remove(file_handler.baseFilename)
            except Exception:
                pass

    @property
    def total(self) -> int:
        return len(self._proxies)

    @property
    def total_working(self) -> int:
        return len(self._working_proxies)

    @property
    def total_bad(self) -> int:
        return len(self._bad_proxies)

    @property
    def proxies(self) -> ProxiesList:
        return self._proxies

    @property
    def bad_proxies(self) -> ProxiesList:
        return self._bad_proxies

    @property
    def working_proxies(self) -> ProxiesList:
        return self._working_proxies

    @working_proxies.setter
    def working_proxies(self, working_proxies: list[Proxy]) -> None:
        self._working_proxies = working_proxies

    def __str__(self) -> str:
        return str(self._proxies)

    def __repr__(self) -> str:
        return self.__str__()

    def read_raw(self) -> List[str]:
        lines = open(self._file_path).readlines()
        return [line.strip().replace("\n", "") for line in lines]

    def random_url(self) -> str:
        return random.choice(self._check_urls)

    def read_with_auth(self) -> None:
        """Format: IP:PORT:USERNAME:PASSWORD"""
        raw_proxies = self.read_raw()
        for proxy in raw_proxies:
            sp_proxy = proxy.split(":")
            ip = sp_proxy[0]
            port = sp_proxy[1]
            username = sp_proxy[2]
            password = sp_proxy[3]
            self._proxies.append(Proxy(ip, port, username, password))

        self._has_auth = True
        if self._shuffle:
            random.shuffle(self._proxies)

    def read_authless(self) -> None:
        """Format: IP:PORT"""
        raw_proxies = self.read_raw()
        for proxy in raw_proxies:
            sp_proxy = proxy.split(":")
            ip = sp_proxy[0]
            port = sp_proxy[1]
            self._proxies.append(Proxy(ip, port))
        logger.debug(f"Loaded total {len(self._proxies)} proxies from {self._file_path}")
        if self._shuffle:
            random.shuffle(self._proxies)

    async def _check_proxy(self, proxy: Proxy, response_time: Optional[int] = None) -> bool:
        limit = 100

        if "win" in sys.platform:
            # It's fucking windows so we need to limit the number of parallel connections now.
            limit = 60

        connector = aiohttp.TCPConnector(limit=limit)
        session = aiohttp.ClientSession(connector=connector)
        url = self.random_url()
        p = proxy.http

        async with self._thread_control:
            logger.debug(f"Checking proxy {p} ..")
            try:
                # resp = await asyncio.wait_for(session.get(url, proxy=p), timeout=self._max_response_time)
                resp = await session.get(url, timeout=self._max_response_time, proxy=p, ssl=False)
                # await resp.read()
                await session.close()

            except asyncio.TimeoutError as e:
                self._timeout_count += 1
                logger.debug(f"{p} : TIMEOUT {e}. {url}")
                self._bad_proxies.append(proxy)
                await session.close()
                return False

            except Exception as e:
                logger.debug(f"Bad proxy raised. {e}", exc_info=self._extra_debug)
                await session.close()
                return False

            if resp.status == 200:
                logger.debug(f"{p}: Working")
                self._working_proxies.append(proxy)

            else:
                logger.debug(f"{p}: Not Working. Response code: {resp.status}")
                self._bad_proxies.append(proxy)

            return True

    async def check_all_proxies(self, max_resp_time: int = 30) -> None:
        """Run this to check all proxies at once."""
        tasks: List[asyncio.Task[bool]] = []
        for proxy in self._proxies:
            tasks.append(asyncio.create_task(self._check_proxy(proxy, max_resp_time)))
        await asyncio.gather(*tasks)
        self._proxies_checked = True
        logger.debug("All proxies checked.")

    async def _check_proxy_socks(self, proxy: Proxy, response_time: Optional[int] = None) -> bool:
        url = "http://www.example.com"
        socks_connector = ProxyConnector.from_url(proxy.socks5)  # type: ignore
        session = aiohttp.ClientSession(connector=socks_connector)
        logger.debug(f"Checking proxy {proxy} ..")
        try:
            resp = await asyncio.wait_for(session.get(url), timeout=response_time)

        except asyncio.TimeoutError:
            logger.debug(f"{proxy} : TIMEOUT: Not working.")
            self._bad_proxies.append(proxy)
            await session.close()
            return False

        except Exception as e:
            logger.debug(f"Bad proxy raised. {e}", exc_info=self._extra_debug)
            await session.close()
            return False

        await resp.read()
        await session.close()
        if resp.status == 200:
            logger.debug(f"{proxy}: Working")
            self._working_proxies.append(proxy)
        else:
            logger.debug(f"{proxy}: Not Working")
            self._bad_proxies.append(proxy)

        return True

    async def check_all_proxies_socks5(self, max_resp_time: int = 5) -> None:
        """Run the check on all proxies at once."""
        tasks: List[asyncio.Task[bool]] = []
        for proxy in self._proxies:
            tasks.append(asyncio.create_task(self._check_proxy_socks(proxy, max_resp_time)))
        await asyncio.gather(*tasks)
        self._proxies_checked = True
        logger.debug("All proxies checked.")

    def get_working_proxies_list_http(self) -> List[str]:
        working_list: List[str] = []
        for proxy in self._working_proxies:
            working_list.append(proxy.http)
        return working_list

    def write_working_proxies(self, filename: str) -> None:
        working_list = self.get_working_proxies_list_http()
        logger.debug(working_list)
        with open(filename, "w") as f:
            f.write("\n".join([proxy.strip() for proxy in working_list]))
        logger.debug(f"Proxies written to: {filename}")

    def get_random_http(self) -> Optional[str]:
        _p = None
        if len(self._working_proxies) > 0:
            proxy = random.choice(self._working_proxies)
            _p = proxy.http
        return _p

    def get_random_socks5(self) -> Optional[str]:
        _p = None
        if len(self._working_proxies) > 0:
            proxy = random.choice(self._working_proxies)
            _p = proxy.socks5
        return _p

    def get_random_socks5_telegram(self) -> Optional[Dict[str, Any]]:
        _p = None
        if len(self._working_proxies) > 0:
            proxy = random.choice(self._working_proxies)
            _p = proxy.telegram_socks5
        return _p

    def next_http_from_list(self) -> Optional[str]:
        """Get next proxy from proxies list"""

        def __iter() -> ProxyiesGen:
            for proxy in self._working_proxies:
                yield proxy

        if self._proxy_iterator is None:
            self._proxy_iterator = __iter()

        return str(next(self._proxy_iterator).http)

    def next_http_from_cycle(self) -> str:
        """Get next proxy from proxies cycle"""

        def __iter() -> ProxyiesGen:
            for proxy in itertools.cycle(self._working_proxies):
                yield proxy

        if self._proxy_iterator_cycle is None:
            self._proxy_iterator_cycle = __iter()

        return str(next(self._proxy_iterator_cycle).http)

    def next_socks5_from_list(self) -> str:
        """Get next proxy from proxies list"""

        if self._proxy_iterator is None:
            self._proxy_iterator = self.__proxies_gen(self._working_proxies)
        return str(next(self._proxy_iterator).socks5)

    def next_socks5_from_cycle(self) -> str:
        """Get next proxy from proxies cycle"""

        if self._proxy_iterator_cycle is None:
            self._proxy_iterator_cycle = self.__proxies_gen(self._working_proxies, cycle_proxies=True)
        return str(next(self._proxy_iterator_cycle).socks5)

    def next_http_telegram_from_list(self) -> Dict[str, Any]:
        """Get next proxy from proxies list"""

        if self._proxy_iterator is None:
            self._proxy_iterator = self.__proxies_gen(self._working_proxies)
        return dict(next(self._proxy_iterator).telegram_http)

    def next_http_telegram_from_cycle(self) -> Dict[str, Any]:
        """Get next proxy from proxies cycle"""

        if self._proxy_iterator is None:
            self._proxy_iterator = self.__proxies_gen(self._working_proxies, cycle_proxies=True)
        return dict(next(self._proxy_iterator).telegram_http)

    def next_socks5_telegram_from_cycle(self) -> Dict[str, Any]:
        """Get next proxy from proxies cycle"""
        if self._proxy_iterator_cycle is None:
            self._proxy_iterator_cycle = self.__proxies_gen(self._working_proxies, cycle_proxies=True)
        return dict(next(self._proxy_iterator_cycle).telegram_socks5)

    def next_socks5_telegram_from_list(self) -> Dict[str, Any]:
        """Get next proxy from proxies cycle"""

        if self._proxy_iterator_cycle is None:
            self._proxy_iterator_cycle = self.__proxies_gen(self._working_proxies)
        return dict(next(self._proxy_iterator_cycle).telegram_socks5)

    def next_https_from_list(self) -> str:
        """Get next proxy from proxies list"""

        if self._proxy_iterator is None:
            self._proxy_iterator = self.__proxies_gen(self._working_proxies)

        return str(next(self._proxy_iterator).https)

    def next_https_from_cycle(self) -> str:
        """Get next proxy from proxies cycle"""

        if not self._proxy_iterator_cycle:
            self._proxy_iterator_cycle = self.__proxies_gen(self._working_proxies, cycle_proxies=True)

        return str(next(self._proxy_iterator_cycle).https)

    def __proxies_gen(self, proxies_list: List[Proxy], cycle_proxies: bool = False) -> ProxyiesGen:
        if cycle_proxies:
            for proxy in itertools.cycle(self._working_proxies):
                yield proxy

        else:
            for proxy in proxies_list:
                yield proxy
