from proxy_reader import ProxiesReader
import asyncio
import time
import sys


async def main() -> None:
    reader = ProxiesReader("proxies.txt", debug=True, extra_debug=True)
    # reader.read_with_auth()
    reader.read_with_auth()
    start = time.time()
    await reader.check_all_proxies()
    end = time.time()
    print(reader.working_proxies, reader.total_working)
    print(f"Time taken: {end- start}")


if __name__ == "__main__":
    if "win" in sys.platform:
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
