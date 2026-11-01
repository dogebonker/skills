"""Factory Method: a creator defers the choice of notifier to a hook method."""
from __future__ import annotations

from typing import Protocol


class Notifier(Protocol):
    def send(self, to: str, text: str) -> str: ...


class EmailNotifier:
    def send(self, to: str, text: str) -> str:
        return f"email to {to}: {text}"


class SmsNotifier:
    def send(self, to: str, text: str) -> str:
        return f"sms to {to}: {text}"


class Alerts:
    """Creator: shared workflow, subclasses pick the product."""

    def make_notifier(self) -> Notifier:
        raise NotImplementedError

    def alert(self, to: str, text: str) -> str:
        return self.make_notifier().send(to, f"ALERT {text}")


class EmailAlerts(Alerts):
    def make_notifier(self) -> Notifier:
        return EmailNotifier()


class SmsAlerts(Alerts):
    def make_notifier(self) -> Notifier:
        return SmsNotifier()


# Often a plain function or a dict of classes is enough.
NOTIFIERS: dict[str, type[Notifier]] = {"email": EmailNotifier, "sms": SmsNotifier}


def make_notifier(kind: str) -> Notifier:
    return NOTIFIERS[kind]()


if __name__ == "__main__":
    for creator in (EmailAlerts(), SmsAlerts()):
        print(creator.alert("ana", "disk full"))
    print(make_notifier("sms").send("bo", "hi"))
