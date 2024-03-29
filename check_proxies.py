from proxy_reader import ProxiesReader
import asyncio
import time
import sys


async def main() -> None:
    reader = ProxiesReader("proxies.txt", debug=False, extra_debug=False)
    # reader.read_with_auth()
    reader.read_with_auth()
    start = time.time()
    await reader.check_all_proxies()
    end = time.time()
    print(reader.working_proxies, reader.total_working)
    print(f"Time taken: {end- start}")


if __name__ == "__main__":
    if "win" in sys.platform:
        """
        Issue with aiohttp on Windows when trying to use the ProactorEventLoop.
        Since Python 3.8, it is now the default event loop on Windows (instead of the SelectorEventLoop),
        so until the the library gets a fix, the workaround is to switch back to SelectorEventLoop explicitly

        Source: https://stackoverflow.com/a/61316457/12631969
        """
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # type: ignore

    asyncio.run(main())
