import asyncio
import logging
import random

import aiohttp
from aiohttp_socks import ProxyConnector

from .constants import (
    CHECK_URLS,
    CONNECT_TIMEOUT,
    DEFAULT_CHECK_THREADS,
    MAX_RESPONSE_TIME,
)
from .logs_config import logger as package_logger
from .models.proxy import Proxy
from .models.results import ProxyCheckResults
from .reader import ProxiesReader
from .utils import parse_proxy_line


class ProxiesChecker:
    def __init__(
        self,
        proxy_checking_threads: int = DEFAULT_CHECK_THREADS,
        max_response_time: int = MAX_RESPONSE_TIME,
        connect_timeout: int = CONNECT_TIMEOUT,
        check_urls: list[str] = [],
        logger: logging.Logger | None = None,
    ) -> None:
        self._thread_control: asyncio.Semaphore = asyncio.Semaphore(
            proxy_checking_threads
        )
        self._max_response_time = max_response_time
        self._connect_timeout = connect_timeout

        self._default_timeout = aiohttp.ClientTimeout(
            total=self._max_response_time,
            connect=self._connect_timeout,
        )

        self._check_urls = check_urls or CHECK_URLS
        self._connector = aiohttp.TCPConnector(
            limit=0, ttl_dns_cache=600, use_dns_cache=True
        )
        self._session: aiohttp.ClientSession | None = None

        self._logger = logger or package_logger

    async def close(self) -> None:
        self._logger.debug("Closing checker resources")
        if self._session:
            await self._session.close()
        await self._connector.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._logger.debug("Creating ClientSession (connector=%s)", self._connector)
            self._session = aiohttp.ClientSession(connector=self._connector)
        else:
            self._logger.debug("Reusing existing ClientSession")
        return self._session

    def _random_proxy_check_url(self) -> str:
        return random.choice(self._check_urls)

    async def _check_proxy(
        self,
        proxy: Proxy,
        response_time: aiohttp.ClientTimeout | None = None,
        check_results: ProxyCheckResults = ProxyCheckResults(),
    ) -> bool:
        async with self._thread_control:
            self._logger.debug("Checking HTTP proxy %s", proxy)
            try:
                session = await self._get_session()
                resp = await session.get(
                    self._random_proxy_check_url(),
                    timeout=response_time,
                    proxy=proxy.http,
                    ssl=False,
                )

                if resp.status in range(200, 300):
                    self._logger.debug("%s: working (status=%s)", proxy, resp.status)
                    check_results.add_working(proxy)
                    return True

                else:
                    self._logger.debug("%s: bad response status=%s", proxy, resp.status)
                    check_results.add_bad(proxy)

            except asyncio.TimeoutError as e:
                self._logger.debug("%s: timeout (%s)", proxy, e)
                check_results.add_timeout(proxy)

            except Exception as e:
                self._logger.debug(
                    "Proxy check failed: %s (%s)", proxy, e, exc_info=True
                )
                check_results.add_error(proxy)

            return False

    async def check_single_proxy(
        self,
        proxy: str,
        max_resp_time: int = MAX_RESPONSE_TIME,
        connect_timeout: int = CONNECT_TIMEOUT,
    ) -> bool:
        self._logger.debug("check_single_proxy: %s", proxy)
        proxy_dict = parse_proxy_line(proxy)
        return await self._check_proxy(
            Proxy(proxy_dict),
            aiohttp.ClientTimeout(total=max_resp_time, connect=connect_timeout),
        )

    async def check_multiple_proxies(
        self,
        proxies: list[Proxy] | ProxiesReader,
        max_resp_time: int = MAX_RESPONSE_TIME,
        connect_timeout: int = CONNECT_TIMEOUT,
    ) -> ProxyCheckResults:
        """Run this to check all proxies at once."""
        proxies_list = (
            proxies.proxies if isinstance(proxies, ProxiesReader) else proxies
        )
        self._logger.debug(
            "check_multiple_proxies: starting %d HTTP checks (threads limited by semaphore)",
            len(proxies_list),
        )
        check_results = ProxyCheckResults()
        async with asyncio.TaskGroup() as gp:
            for proxy in proxies_list:
                gp.create_task(
                    self._check_proxy(
                        proxy,
                        aiohttp.ClientTimeout(
                            total=max_resp_time, connect=connect_timeout
                        ),
                        check_results,
                    )
                )
        self._logger.debug(
            "check_multiple_proxies: done working=%d bad=%d timeout=%d error=%d",
            check_results.working_count,
            check_results.bad_count,
            check_results.timeout_count,
            check_results.error_count,
        )
        return check_results

    async def _check_proxy_socks(
        self,
        proxy: Proxy,
        response_time: int = MAX_RESPONSE_TIME,
        connect_timeout: int = CONNECT_TIMEOUT,
        check_results: ProxyCheckResults = ProxyCheckResults(),
    ) -> bool:
        url = self._random_proxy_check_url()
        self._logger.debug("Checking SOCKS5 proxy %s via %s", proxy, url)
        socks_connector = ProxyConnector.from_url(proxy.socks5)  # type: ignore
        session = aiohttp.ClientSession(connector=socks_connector)  # type: ignore
        try:
            resp = await asyncio.wait_for(
                session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(
                        total=response_time, connect=connect_timeout
                    ),
                ),
                timeout=response_time,
            )

        except asyncio.TimeoutError:
            self._logger.debug("%s: SOCKS5 timeout", proxy)
            check_results.add_timeout(proxy)
            await session.close()
            return False

        except Exception as e:
            self._logger.debug("SOCKS5 check failed: %s (%s)", proxy, e, exc_info=True)
            check_results.add_error(proxy)
            await session.close()
            return False

        await resp.read()
        await session.close()
        if resp.status == 200:
            self._logger.debug("%s: SOCKS5 working (status=200)", proxy)
            check_results.add_working(proxy)
        else:
            self._logger.debug("%s: SOCKS5 bad status=%s", proxy, resp.status)
            check_results.add_bad(proxy)

        return True

    async def check_multiple_proxies_socks5(
        self,
        proxies: list[Proxy] | ProxiesReader,
        max_resp_time: int = MAX_RESPONSE_TIME,
        connect_timeout: int = CONNECT_TIMEOUT,
    ) -> None:
        """Run the check on all proxies at once."""
        tasks: list[asyncio.Task[bool]] = []
        proxies_list = (
            proxies.proxies if isinstance(proxies, ProxiesReader) else proxies
        )
        self._logger.debug(
            "check_multiple_proxies_socks5: scheduling %d checks", len(proxies_list)
        )
        for proxy in proxies_list:
            tasks.append(
                asyncio.create_task(
                    self._check_proxy_socks(
                        proxy,
                        max_resp_time,
                        connect_timeout,
                    )
                )
            )
        await asyncio.gather(*tasks)
        self._proxies_checked = True
        self._logger.debug(
            "check_multiple_proxies_socks5: finished %d tasks", len(tasks)
        )
