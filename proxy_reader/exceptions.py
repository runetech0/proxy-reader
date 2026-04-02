class ProxyReaderError(Exception):
    """Base exception for all proxy reader exceptions."""


class NoMoreProxiesError(ProxyReaderError):
    """Raised when there are no more proxies available in result."""
