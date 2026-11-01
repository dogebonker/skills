"""DIP: the order policy owns the abstraction it needs; the SMS detail plugs in. Same output."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Order:
    id: str
    phone: str
    total_cents: int


# Every line the gateway sends, so the demo can compare the two versions.
SMS_LOG: list[str] = []


class SmsGateway:
    """A low-level detail. In a real app this lives in an infrastructure module."""

    def send(self, phone: str, text: str) -> None:
        line = f"  [sms {phone}] {text}"
        SMS_LOG.append(line)
        print(line)


def confirmation(order: Order) -> str:
    return f"Order {order.id} confirmed: {order.total_cents / 100:.2f}"


# --- Violation: business policy constructs and depends on a concrete transport.
class OrderServiceV1:
    def __init__(self) -> None:
        self._sms = SmsGateway()

    def place(self, order: Order) -> str:
        self._sms.send(order.phone, confirmation(order))
        return order.id


# --- Fix: the policy declares the port it needs and receives an implementation.
class OrderNotifier(Protocol):
    def order_confirmed(self, phone: str, text: str) -> None: ...


class OrderService:
    def __init__(self, notifier: OrderNotifier) -> None:
        self._notifier = notifier

    def place(self, order: Order) -> str:
        self._notifier.order_confirmed(order.phone, confirmation(order))
        return order.id


class SmsOrderNotifier:
    """Adapter from the port to the detail; satisfies OrderNotifier without inheriting it."""

    def __init__(self, gateway: SmsGateway) -> None:
        self._gateway = gateway

    def order_confirmed(self, phone: str, text: str) -> None:
        self._gateway.send(phone, text)


class RecordingNotifier:
    def __init__(self) -> None:
        self.sent: list[str] = []

    def order_confirmed(self, phone: str, text: str) -> None:
        self.sent.append(text)


if __name__ == "__main__":
    order = Order("A-1042", "+351900000000", 3599)
    print("violation:")
    OrderServiceV1().place(order)
    violation_sent = SMS_LOG.copy()
    SMS_LOG.clear()
    # Composition root: the only place that knows the concrete detail.
    print("fix:")
    OrderService(SmsOrderNotifier(SmsGateway())).place(order)
    print("same output:", violation_sent == SMS_LOG)
    fake = RecordingNotifier()
    OrderService(fake).place(order)
    print("fix with fake:", fake.sent)
