import random
import itertools
from .proxy import Proxy
from typing import *
import aiohttp
import asyncio
from .logger import logger, console_handler, file_handler
import os
import aiosocksy
from aiosocksy.connector import ProxyConnector, ProxyClientRequest


class TypesDefs:
    ProxiesList = List[Proxy]


class ProxiesReader:
    def __init__(self, file_path="./proxies.txt", shuffle=False, debug=False, extra_debug=False):
        self._file_path = file_path
        self.debug = debug
        self.extra_debug = extra_debug
        if not self.debug:
            os.remove(file_handler.baseFilename)
            logger.removeHandler(file_handler)
            logger.removeHandler(console_handler)
        self.shuffle = shuffle
        self.proxies: TypesDefs.ProxiesList = []
        self.has_auth = False
        self.bad_proxies: TypesDefs.ProxiesList = []
        self.working_proxies: TypesDefs.ProxiesList = []
        self.proxies_checked = False
        self._proxy_iterator = None
        self._proxy_iterator_cycle = None

    @property
    def total(self):
        return len(self.proxies)

    @property
    def total_working(self):
        return len(self.working_proxies)

    @property
    def total_bad(self):
        return len(self.bad_proxies)

    def __repr__(self):
        return str(self.proxies)

    def read_raw(self):
        return open(self._file_path).readlines()

    def read_with_auth(self):
        """Format: IP:PORT:USERNAME:PASSWORD"""
        raw_proxies = self.read_raw()
        for proxy in raw_proxies:
            sp_proxy = proxy.split(":")
            ip = sp_proxy[0]
            port = sp_proxy[1]
            username = sp_proxy[2]
            password = sp_proxy[3]
            self.proxies.append(Proxy(ip, port, username, password))
        self.has_auth = True
        if self.shuffle:
            random.shuffle(self.proxies)

    def read_authless(self):
        """Format: IP:PORT"""
        raw_proxies = self.read_raw()
        for proxy in raw_proxies:
            sp_proxy = proxy.split(":")
            ip = sp_proxy[0]
            port = sp_proxy[1]
            self.proxies.append(Proxy(ip, port))
        logger.debug(
            f"Loaded total {len(self.proxies)} proxies from {self._file_path}")
        if self.shuffle:
            random.shuffle(self.proxies)

    async def _check_proxy(self, proxy: Proxy, response_time: int = None):
        p = proxy.http
        logger.debug(f"Checking proxy {p} ..")
        url = "https://www.example.com"
        session = aiohttp.ClientSession()
        try:
            resp = await asyncio.wait_for(session.get(url, proxy=p), timeout=response_time)
        except asyncio.TimeoutError:
            logger.debug(f"{p} : TIMEOUT: Not working.")
            self.bad_proxies.append(proxy)
            await session.close()
            return False
        except Exception as e:
            logger.debug(f"Bad proxy raised. {e}", exc_info=self.extra_debug)
            await session.close()
            return False
        await resp.read()
        await session.close()
        if resp.status == 200:
            logger.debug(f"{p}: Working")
            self.working_proxies.append(proxy)
        else:
            logger.debug(f"{p}: Not Working")
            self.bad_proxies.append(proxy)

    async def check_all_proxies(self, max_resp_time: int = 5):
        """Run this to check all proxies at once."""
        tasks = []
        for proxy in self.proxies:
            tasks.append(asyncio.create_task(
                self._check_proxy(proxy, max_resp_time)))
        await asyncio.gather(*tasks)
        self.proxies_checked = True
        logger.debug(f"All proxies checked.")

    async def _check_proxy_socks(self, proxy: Proxy, response_time: int = None):
        url = "https://www.example.com"
        if proxy.username is not None and proxy.password is not None:
            auth = aiosocksy.Socks5Auth(proxy.username, proxy.password)
        else:
            auth = None
        socks_connector = ProxyConnector()
        session = aiohttp.ClientSession(
            connector=socks_connector, request_class=ProxyClientRequest)
        logger.debug(f"Checking proxy {proxy} ..")
        try:
            resp = await asyncio.wait_for(session.get(url, proxy=proxy.socks5, proxy_auth=auth), timeout=response_time)
        except asyncio.TimeoutError:
            logger.debug(f"{proxy} : TIMEOUT: Not working.")
            self.bad_proxies.append(proxy)
            await session.close()
            return False
        except Exception as e:
            logger.debug(f"Bad proxy raised. {e}", exc_info=self.extra_debug)
            await session.close()
            return False
        await resp.read()
        await session.close()
        if resp.status == 200:
            logger.debug(f"{proxy}: Working")
            self.working_proxies.append(proxy)
        else:
            logger.debug(f"{proxy}: Not Working")
            self.bad_proxies.append(proxy)

    async def check_all_proxies_socks5(self, max_resp_time: int = 5):
        """Run the check on all proxies at once."""
        tasks = []
        for proxy in self.proxies:
            tasks.append(asyncio.create_task(
                self._check_proxy_socks(proxy, max_resp_time)))
        await asyncio.gather(*tasks)
        self.proxies_checked = True
        logger.debug(f"All proxies checked.")

    def get_working_proxies_list_http(self):
        working_list = []
        for proxy in self.working_proxies:
            if self.has_auth:
                working_list.append(
                    f"{proxy.ip}:{proxy.port}:{proxy.username}:{proxy.password}")
            else:
                working_list.append(f"{proxy.ip}:{proxy.port}")
        return working_list

    def write_working_proxies(self, filename: str):
        working_list = self.get_working_proxies_list_http()
        logger.debug(working_list)
        with open(filename, "w") as f:
            f.write("\n".join([proxy.strip() for proxy in working_list]))
        logger.debug(f"Proxies written to: {filename}")

    def get_random_http(self) -> str:
        if len(self.working_proxies) > 0:
            proxy = random.choice(self.working_proxies)
            return proxy.http

    def get_random_socks5(self) -> str:
        if len(self.working_proxies) > 0:
            proxy = random.choice(self.working_proxies)
            return proxy.socks5

    def get_random_socks5_telegram(self) -> str:
        if len(self.working_proxies) > 0:
            proxy = random.choice(self.working_proxies)
            return proxy.telegram_socks5

    def next_http_from_list(self) -> str:
        """Get next proxy from proxies list"""
        def __iter():
            for proxy in self.working_proxies:
                yield proxy

        if self._proxy_iterator is None:
            self._proxy_iterator = __iter()
        return next(self._proxy_iterator).http

    def next_http_from_cycle(self) -> str:
        """Get next proxy from proxies cycle"""
        def __iter():
            for proxy in itertools.cycle(self.working_proxies):
                yield proxy

        if self._proxy_iterator_cycle is None:
            self._proxy_iterator_cycle = __iter()
        return next(self._proxy_iterator_cycle).http

    def next_socks5_from_list(self) -> str:
        """Get next proxy from proxies list"""
        def __iter():
            for proxy in self.working_proxies:
                yield proxy

        if self._proxy_iterator is None:
            self._proxy_iterator = __iter()
        return next(self._proxy_iterator).socks5

    def next_socks5_from_cycle(self) -> str:
        """Get next proxy from proxies cycle"""
        def __iter():
            for proxy in itertools.cycle(self.working_proxies):
                yield proxy

        if self._proxy_iterator_cycle is None:
            self._proxy_iterator_cycle = __iter()
        return next(self._proxy_iterator_cycle).socks5

    def next_http_telegram_from_list(self) -> str:
        """Get next proxy from proxies list"""
        def __iter():
            for proxy in self.working_proxies:
                yield proxy

        if self._proxy_iterator is None:
            self._proxy_iterator = __iter()
        return next(self._proxy_iterator).telegram_http

    def next_http_telegram_from_cycle(self) -> str:
        """Get next proxy from proxies cycle"""
        def __iter():
            for proxy in itertools.cycle(self.working_proxies):
                yield proxy

        if self._proxy_iterator is None:
            self._proxy_iterator = __iter()
        return next(self._proxy_iterator).telegram_http

    def next_socks5_telegram_from_cycle(self) -> str:
        """Get next proxy from proxies cycle"""
        def __iter():
            for proxy in itertools.cycle(self.working_proxies):
                yield proxy

        if self._proxy_iterator_cycle is None:
            self._proxy_iterator_cycle = __iter()
        return next(self._proxy_iterator_cycle).telegram_socks5

    def next_socks5_telegram_from_list(self) -> str:
        """Get next proxy from proxies cycle"""
        def __iter():
            for proxy in self.working_proxies:
                yield proxy

        if self._proxy_iterator_cycle is None:
            self._proxy_iterator_cycle = __iter()
        return next(self._proxy_iterator_cycle).telegram_socks5

    def next_https_from_list(self) -> str:
        """Get next proxy from proxies list"""
        def __iter():
            for proxy in self.working_proxies:
                yield proxy

        if self._proxy_iterator is None:
            self._proxy_iterator = __iter()
        return next(self._proxy_iterator).https

    def next_https_from_cycle(self) -> str:
        """Get next proxy from proxies cycle"""
        def __iter():
            for proxy in itertools.cycle(self.working_proxies):
                yield proxy

        if self._proxy_iterator_cycle is None:
            self._proxy_iterator_cycle = __iter()
        return next(self._proxy_iterator_cycle).https
