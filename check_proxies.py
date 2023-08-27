from proxy_reader import ProxiesReader
import asyncio
import time


async def main() -> None:
    reader = ProxiesReader("proxies.txt", debug=True)
    # reader.read_with_auth()
    reader.read_with_auth()
    start = time.time()
    await reader.check_all_proxies()
    end = time.time()
    print(reader.working_proxies, reader.total_working)
    print(f"Time taken: {end- start}")


if __name__ == "__main__":
    asyncio.run(main())
