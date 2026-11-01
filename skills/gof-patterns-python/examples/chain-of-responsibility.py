"""Chain of Responsibility: each handler acts or passes the request on."""
from __future__ import annotations

from typing import Callable, Optional

Request = dict[str, str]
Handler = Callable[[Request], Optional[str]]  # None means "not mine, continue"


def require_auth(req: Request) -> str | None:
    return None if "token" in req else "401 unauthorized"


def rate_limit(req: Request) -> str | None:
    return "429 slow down" if req.get("user") == "spammer" else None


def route(req: Request) -> str | None:
    return f"200 ok {req['path']}"


def run_chain(handlers: list[Handler], req: Request) -> str:
    for handler in handlers:
        result = handler(req)
        if result is not None:
            return result
    return "404 nobody handled it"


if __name__ == "__main__":
    chain = [require_auth, rate_limit, route]
    print(run_chain(chain, {"path": "/a"}))
    print(run_chain(chain, {"path": "/a", "token": "t", "user": "spammer"}))
    print(run_chain(chain, {"path": "/a", "token": "t", "user": "ana"}))
