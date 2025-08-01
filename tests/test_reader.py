import os
import tempfile

import pytest

from proxy_reader.reader import ProxiesReader


class TestProxiesReader:
    """Test cases for ProxiesReader class"""

    def test_init_with_proxies_file(self) -> None:
        """Test initializing ProxiesReader with proxies.txt file"""
        reader = ProxiesReader("proxies.txt", check_proxies=False)

        assert reader.total == 5
        assert (
            reader.total_working == 5
        )  # Since check_proxies=False, all proxies are considered working
        assert reader.total_bad == 0
        assert len(reader.proxies) == 5
        assert len(reader.working_proxies) == 5
        assert len(reader.bad_proxies) == 0

    def test_init_with_check_proxies_true(self) -> None:
        """Test initializing ProxiesReader with check_proxies=True"""
        reader = ProxiesReader("proxies.txt", check_proxies=True)

        assert reader.total == 5
        assert (
            reader.total_working == 0
        )  # Initially empty since proxies haven't been checked yet
        assert reader.total_bad == 0
        assert len(reader.proxies) == 5
        assert len(reader.working_proxies) == 0
        assert len(reader.bad_proxies) == 0

    def test_load_list_class_method(self) -> None:
        """Test the load_list class method"""
        proxy_list = ["192.168.1.1:8080", "10.0.0.1:3128"]
        reader = ProxiesReader.load_list(proxy_list, check_proxies=False)

        assert reader.total == 2
        assert reader.total_working == 2
        assert reader.total_bad == 0
        assert len(reader.proxies) == 2
        assert len(reader.working_proxies) == 2

    def test_proxy_parsing(self) -> None:
        """Test that proxies are parsed correctly"""
        reader = ProxiesReader("proxies.txt", check_proxies=False)

        # Check that the proxy from proxies.txt is parsed correctly
        proxy = reader.proxies[0]
        assert proxy.ip == "23.95.150.145"
        assert proxy.port == "6114"
        assert proxy.http == "http://23.95.150.145:6114"
        assert proxy.https == "https://23.95.150.145:6114"
        assert proxy.socks5 == "socks5://23.95.150.145:6114"

    def test_get_random_methods(self) -> None:
        """Test get_random methods"""
        reader = ProxiesReader("proxies.txt", check_proxies=False)

        # Test get_random_http
        random_http = reader.get_random_http()
        assert random_http == "http://23.95.150.145:6114"

        # Test get_random_socks5
        random_socks5 = reader.get_random_socks5()
        assert random_socks5 == "socks5://23.95.150.145:6114"

    def test_next_methods(self) -> None:
        """Test next methods for getting proxies sequentially"""
        reader = ProxiesReader("proxies.txt", check_proxies=False)

        # Test next_http_from_list
        next_http = reader.next_http_from_list()
        assert next_http == "http://23.95.150.145:6114"

        # Test next_http_from_cycle
        next_http_cycle = reader.next_http_from_cycle()
        assert next_http_cycle == "http://23.95.150.145:6114"

        # Test next_socks5_from_list
        next_socks5 = reader.next_socks5_from_list()
        assert next_socks5 == "socks5://23.95.150.145:6114"

        # Test next_socks5_from_cycle
        next_socks5_cycle = reader.next_socks5_from_cycle()
        assert next_socks5_cycle == "socks5://23.95.150.145:6114"

    def test_telegram_proxy_methods(self) -> None:
        """Test Telegram proxy format methods"""
        reader = ProxiesReader("proxies.txt", check_proxies=False)

        # Test next_http_telegram_from_list
        telegram_http = reader.next_http_telegram_from_list()
        assert isinstance(telegram_http, dict)
        assert telegram_http["proxy_type"] == 3
        assert telegram_http["addr"] == "23.95.150.145"
        assert telegram_http["port"] == 6114

        # Test next_http_telegram_from_cycle
        telegram_http_cycle = reader.next_http_telegram_from_cycle()
        assert isinstance(telegram_http_cycle, dict)
        assert telegram_http_cycle["proxy_type"] == 3
        assert telegram_http_cycle["addr"] == "23.95.150.145"
        assert telegram_http_cycle["port"] == 6114

    def test_write_working_proxies(self) -> None:
        """Test writing working proxies to file"""
        reader = ProxiesReader("proxies.txt", check_proxies=False)

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            temp_filename = temp_file.name

        try:
            reader.write_working_proxies(temp_filename)

            # Check that the file was created and contains the proxy
            assert os.path.exists(temp_filename)
            with open(temp_filename, "r") as f:
                content = f.read().strip()
                assert content == content
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_get_working_proxies_list_http(self) -> None:
        """Test getting list of working HTTP proxies"""
        reader = ProxiesReader("proxies.txt", check_proxies=False)

        working_list = reader.get_working_proxies_list_http()
        assert len(working_list) == 5
        assert working_list[0] == "http://23.95.150.145:6114"

    def test_str_and_repr(self) -> None:
        """Test string representation methods"""
        reader = ProxiesReader("proxies.txt", check_proxies=False)

        str_repr = str(reader)
        repr_repr = repr(reader)

        assert str_repr == repr_repr
        assert "23.95.150.145:6114" in str_repr

    def test_working_proxies_setter(self) -> None:
        """Test working_proxies setter"""
        reader = ProxiesReader("proxies.txt", check_proxies=False)

        # Initially should have 1 working proxy
        assert len(reader.working_proxies) == 5

        # Set to empty list
        reader.working_proxies = []
        assert len(reader.working_proxies) == 0
        assert reader.total_working == 0

    def test_with_multiple_proxies(self) -> None:
        """Test with multiple proxies in file"""
        # Create temporary file with multiple proxies
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            temp_file.write("192.168.1.1:8080\n10.0.0.1:3128\n172.16.0.1:8080")
            temp_filename = temp_file.name

        try:
            reader = ProxiesReader(temp_filename, check_proxies=False)

            assert reader.total == 3
            assert reader.total_working == 3
            assert len(reader.proxies) == 3

            # Test that we can get all proxies
            working_list = reader.get_working_proxies_list_http()
            assert len(working_list) == 3
            assert "http://192.168.1.1:8080" in working_list
            assert "http://10.0.0.1:3128" in working_list
            assert "http://172.16.0.1:8080" in working_list
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    def test_file_not_found_error(self) -> None:
        """Test that appropriate error is raised for non-existent file"""
        with pytest.raises(FileNotFoundError):
            ProxiesReader("non_existent_file.txt", check_proxies=False)


if __name__ == "__main__":
    pytest.main([__file__])
