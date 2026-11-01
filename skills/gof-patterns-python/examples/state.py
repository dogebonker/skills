"""State: an Enum plus a transition table beats one class per state when behavior is thin."""
from __future__ import annotations

from enum import Enum, auto


class OrderState(Enum):
    NEW = auto()
    PAID = auto()
    SHIPPED = auto()
    CANCELLED = auto()


TRANSITIONS: dict[tuple[OrderState, str], OrderState] = {
    (OrderState.NEW, "pay"): OrderState.PAID,
    (OrderState.NEW, "cancel"): OrderState.CANCELLED,
    (OrderState.PAID, "ship"): OrderState.SHIPPED,
    (OrderState.PAID, "cancel"): OrderState.CANCELLED,
}


class Order:
    def __init__(self) -> None:
        self.state = OrderState.NEW

    def handle(self, event: str) -> None:
        try:
            self.state = TRANSITIONS[(self.state, event)]
        except KeyError:
            raise ValueError(f"cannot {event} when {self.state.name}") from None


if __name__ == "__main__":
    order = Order()
    for ev in ("pay", "ship"):
        order.handle(ev)
        print(order.state.name)
    try:
        order.handle("cancel")
    except ValueError as e:
        print(e)
