import asyncio
import random
import sys

import aiohttp
from aiohttp_socks import ProxyConnector

from .constants import (
    CHECK_URLS,
    CONNECT_TIMEOUT,
    DEFAULT_CHECK_THREADS,
    MAX_RESPONSE_TIME,
)
from .logs_config import logger
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
        self._connections_limit = 60 if "win" in sys.platform else 100
        self._connector = aiohttp.TCPConnector(limit=self._connections_limit)
        self._session: aiohttp.ClientSession | None = None

    async def close(self) -> None:
        if self._session:
            await self._session.close()
        await self._connector.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(connector=self._connector)
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
            logger.debug(f"Checking proxy {proxy} ..")
            try:
                session = await self._get_session()
                resp = await session.get(
                    self._random_proxy_check_url(),
                    timeout=response_time,
                    proxy=proxy.http,
                    ssl=False,
                )

                if resp.status in range(200, 300):
                    logger.debug(f"{proxy}: Working")
                    check_results.add_working(proxy)
                    return True

                else:
                    logger.debug(f"{proxy}: Not Working. Response code: {resp.status}")
                    check_results.add_bad(proxy)

            except asyncio.TimeoutError as e:
                logger.debug(f"{proxy} : TIMEOUT {e}.")
                check_results.add_timeout(proxy)

            except Exception as e:
                logger.debug(f"Bad proxy raised. {e}", exc_info=True)
                check_results.add_error(proxy)

            return False

    async def check_single_proxy(
        self,
        proxy: str,
        max_resp_time: int = MAX_RESPONSE_TIME,
        connect_timeout: int = CONNECT_TIMEOUT,
    ) -> bool:
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
        return check_results

    async def _check_proxy_socks(
        self,
        proxy: Proxy,
        response_time: int = MAX_RESPONSE_TIME,
        connect_timeout: int = CONNECT_TIMEOUT,
        check_results: ProxyCheckResults = ProxyCheckResults(),
    ) -> bool:
        url = self._random_proxy_check_url()
        socks_connector = ProxyConnector.from_url(proxy.socks5)  # type: ignore
        session = aiohttp.ClientSession(connector=socks_connector)  # type: ignore
        logger.debug(f"Checking proxy {proxy} ..")
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
            logger.debug(f"{proxy} : TIMEOUT: Not working.")
            check_results.add_timeout(proxy)
            await session.close()
            return False

        except Exception as e:
            logger.debug(f"Bad proxy raised. {e}", exc_info=True)
            check_results.add_error(proxy)
            await session.close()
            return False

        await resp.read()
        await session.close()
        if resp.status == 200:
            logger.debug(f"{proxy}: Working")
            check_results.add_working(proxy)
        else:
            logger.debug(f"{proxy}: Not Working")
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
        logger.debug("All proxies checked.")
