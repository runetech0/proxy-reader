import unittest
from proxy_reader.reader import ReadProxies


class TestProxyReader(unittest.TestCase):
    def test_with_auth(self):
        proxies = ReadProxies(file_path="auth_proxies.txt", has_auth=True)

    def test_without_auth(self):
        proxies = ReadProxies(file_path="auth_proxies.txt")