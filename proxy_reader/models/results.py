from .proxy import Proxy


class ProxyCheckResults:
    def __init__(self) -> None:
        self._working: list[Proxy] = []
        self._bad: list[Proxy] = []
        self._timeout: list[Proxy] = []
        self._error: list[Proxy] = []

    @property
    def all(self) -> list[Proxy]:
        return self._working + self._bad + self._timeout + self._error

    @property
    def working(self) -> list[Proxy]:
        return self._working

    @property
    def bad(self) -> list[Proxy]:
        return self._bad

    @property
    def timeout(self) -> list[Proxy]:
        return self._timeout

    @property
    def error(self) -> list[Proxy]:
        return self._error

    @property
    def total_count(self) -> int:
        return len(self.all)

    @property
    def working_count(self) -> int:
        return len(self._working)

    @property
    def bad_count(self) -> int:
        return len(self._bad)

    @property
    def timeout_count(self) -> int:
        return len(self._timeout)

    @property
    def error_count(self) -> int:
        return len(self._error)

    def add_error(self, proxy: Proxy) -> None:
        self._error.append(proxy)

    def add_timeout(self, proxy: Proxy) -> None:
        self._timeout.append(proxy)

    def add_bad(self, proxy: Proxy) -> None:
        self._bad.append(proxy)

    def add_working(self, proxy: Proxy) -> None:
        self._working.append(proxy)

    def __repr__(self) -> str:
        return f"ProxyCheckResults(working={self.working_count}, bad={self.bad_count}, timeout={self.timeout_count}, error={self.error_count})"

    def __str__(self) -> str:
        return self.__repr__()
