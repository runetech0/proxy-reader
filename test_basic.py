#!/usr/bin/env python3
"""Basic test for ProxiesReader functionality"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from proxy_reader.reader import ProxiesReader


def test_basic_functionality() -> bool:
    """Test basic functionality of ProxiesReader"""
    print("Testing ProxiesReader with proxies.txt...")

    # Test initialization
    reader = ProxiesReader("proxies.txt", check_proxies=False)

    print(f"Total proxies: {reader.total}")
    print(f"Working proxies: {reader.total_working}")
    print(f"Bad proxies: {reader.total_bad}")

    # Test proxy parsing
    if reader.proxies:
        proxy = reader.proxies[0]
        print(f"First proxy - IP: {proxy.ip}, Port: {proxy.port}")
        print(f"HTTP URL: {proxy.http}")
        print(f"HTTPS URL: {proxy.https}")
        print(f"SOCKS5 URL: {proxy.socks5}")

    # Test random proxy methods
    random_http = reader.get_random_http()
    print(f"Random HTTP proxy: {random_http}")

    random_socks5 = reader.get_random_socks5()
    print(f"Random SOCKS5 proxy: {random_socks5}")

    # Test next methods
    next_http = reader.next_http_from_list()
    print(f"Next HTTP proxy: {next_http}")

    # Test working proxies list
    working_list = reader.get_working_proxies_list_http()
    print(f"Working proxies list: {working_list}")

    print("All basic tests passed!")
    return True


if __name__ == "__main__":
    try:
        result: bool = test_basic_functionality()
        if result:
            print("\n✅ Basic functionality test completed successfully!")
        else:
            print("\n❌ Basic functionality test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
