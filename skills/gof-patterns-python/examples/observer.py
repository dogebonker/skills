"""Observer: subscribers are plain callables registered on a subject."""
from __future__ import annotations

from typing import Callable

Listener = Callable[[str, float], None]


class PriceFeed:
    def __init__(self) -> None:
        self._listeners: list[Listener] = []

    def subscribe(self, fn: Listener) -> Callable[[], None]:
        self._listeners.append(fn)
        active = True

        def unsubscribe() -> None:
            nonlocal active
            if active:  # a second call is harmless and never removes another subscription
                active = False
                self._listeners.remove(fn)

        return unsubscribe

    def publish(self, symbol: str, price: float) -> None:
        for fn in list(self._listeners):  # copy: listeners may unsubscribe
            fn(symbol, price)


class Alerter:
    def __init__(self, limit: float) -> None:
        self.limit = limit

    def on_price(self, symbol: str, price: float) -> None:
        if price > self.limit:
            print(f"ALERT {symbol} at {price}")


if __name__ == "__main__":
    feed = PriceFeed()
    feed.subscribe(lambda s, p: print(f"log {s} {p}"))
    unsubscribe = feed.subscribe(Alerter(100).on_price)
    feed.publish("ACME", 120.0)
    unsubscribe()
    unsubscribe()
    feed.publish("ACME", 130.0)
