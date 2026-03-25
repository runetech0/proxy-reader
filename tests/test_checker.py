import asyncio

from proxy_reader.checker import ProxiesChecker
from proxy_reader.logs_config import enable_debug_logs
from proxy_reader.reader import ProxiesReader

enable_debug_logs()


async def main() -> None:
    reader = await ProxiesReader.read_proxies_from_file("proxies.txt")
    checker = ProxiesChecker(max_response_time=3)
    check_results = await checker.check_multiple_proxies(reader, max_resp_time=3)
    print(check_results.working_count, check_results.bad_count)
    await checker.close()


if __name__ == "__main__":
    asyncio.run(main())
