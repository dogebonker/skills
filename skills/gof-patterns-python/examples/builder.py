"""Builder: assemble an immutable request step by step, validating at build()."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: str | None


@dataclass
class RequestBuilder:
    _method: str = "GET"
    _url: str = ""
    _headers: dict[str, str] = field(default_factory=dict)
    _body: str | None = None

    def method(self, m: str) -> RequestBuilder:
        self._method = m
        return self

    def url(self, u: str) -> RequestBuilder:
        self._url = u
        return self

    def header(self, k: str, v: str) -> RequestBuilder:
        self._headers[k] = v
        return self

    def body(self, b: str) -> RequestBuilder:
        self._body = b
        return self

    def build(self) -> HttpRequest:
        if not self._url:
            raise ValueError("url is required")
        return HttpRequest(self._method, self._url, dict(self._headers), self._body)


if __name__ == "__main__":
    req = (
        RequestBuilder()
        .method("POST")
        .url("https://api.example.com/orders")
        .header("Content-Type", "application/json")
        .body('{"sku": "A1"}')
        .build()
    )
    print(req)
    # Keyword arguments on a dataclass cover most cases without a builder:
    print(HttpRequest("GET", "https://example.com", {}, None))
