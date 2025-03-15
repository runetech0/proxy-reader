from ._types import ProxyDictT
import re
from typing import cast
from .logs_config import logger


def parse_proxy_line(proxy: str) -> ProxyDictT:
    """
    Detects the format of the proxy string and extracts the components.

    Returns a dictionary with 'ip_or_host', 'port', 'username', and 'password'.
    """
    logger.info("Reading the proxy format ...")
    patterns: list[str] = [
        # Format 1: IP/Hostname:PORT:USERNAME:PASSWORD
        r"^(?P<host>[\w\.-]+):(?P<port>\d+):(?P<username>[^:]+):(?P<password>.+)$",
        # Format 2: USERNAME:PASSWORD:IP/Hostname:PORT
        r"^(?P<username>[^:]+):(?P<password>[^:]+):(?P<host>[\w\.-]+):(?P<port>\d+)$",
        # Format 3: http://USERNAME:PASSWORD@IP/Hostname:PORT
        r"^http:\/\/(?P<username>[^:]+):(?P<password>[^@]+)@(?P<host>[\w\.-]+):(?P<port>\d+)$",
        # Format 4: USERNAME:PASSWORD@IP/Hostname:PORT
        r"^(?P<username>[^:]+):(?P<password>[^@]+)@(?P<host>[\w\.-]+):(?P<port>\d+)$",
        # Format 5: IP/Hostname:PORT (No Username/Password)
        r"^(?P<ip_or_host>[\w\.-]+):(?P<port>\d+)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, proxy.strip())
        if match:
            data = match.groupdict()
            data.setdefault("username", None)  # Ensure username exists
            data.setdefault("password", None)  # Ensure password exists
            return cast(ProxyDictT, data)

    raise ValueError(f"Invalid format: {proxy}")
