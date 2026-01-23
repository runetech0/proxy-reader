import asyncio

from proxy_reader.reader import ProxiesReader


async def main() -> None:
    check_urls = ["https://proxy-check.queuetools.com"]
    reader = ProxiesReader("proxies.txt", check_proxies=True, check_urls=check_urls)
    await reader.check_all_proxies(max_resp_time=3)

    print("Total working proxies:", reader.total_working)
    print("Total bad proxies:", reader.total_bad)
    print("Total proxies:", reader.total)


if __name__ == "__main__":
    asyncio.run(main())
