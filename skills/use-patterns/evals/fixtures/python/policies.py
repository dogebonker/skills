from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

@dataclass
class CarPolicy:
    holder: str
    car_value: float
    driver_age: int

@dataclass
class HomePolicy:
    holder: str
    rebuild_cost: float
    flood_zone: bool

@dataclass
class TravelPolicy:
    holder: str
    trip_days: int
    destination: str

def premium(policy) -> float:
    if isinstance(policy, CarPolicy):
        base = policy.car_value * 0.04
        return base * 1.5 if policy.driver_age < 25 else base
    elif isinstance(policy, HomePolicy):
        return policy.rebuild_cost * 0.002 + (300 if policy.flood_zone else 0)
    elif isinstance(policy, TravelPolicy):
        return 8 + policy.trip_days * 1.75
    raise TypeError(f"unknown policy {policy!r}")

def describe(policy) -> str:
    if isinstance(policy, CarPolicy):
        return f"Car cover for {policy.holder}, value {policy.car_value:.0f}"
    elif isinstance(policy, HomePolicy):
        return f"Home cover for {policy.holder}, rebuild {policy.rebuild_cost:.0f}"
    elif isinstance(policy, TravelPolicy):
        return f"Travel cover for {policy.holder}, {policy.trip_days} days in {policy.destination}"
    raise TypeError(f"unknown policy {policy!r}")

def claim_limit(policy) -> float:
    if isinstance(policy, CarPolicy):
        return policy.car_value
    elif isinstance(policy, HomePolicy):
        return policy.rebuild_cost * 1.1
    elif isinstance(policy, TravelPolicy):
        return 5000.0
    raise TypeError(f"unknown policy {policy!r}")

def tax_rate(region: str) -> float:
    if region == "north":
        return 0.21
    elif region == "south":
        return 0.19
    elif region == "islands":
        return 0.12
    return 0.20

def parse_claim_form(form: dict) -> dict:
    amount = float(form["amount"])
    if amount <= 0 or amount > 250000:
        raise ValueError("amount must be between 0 and 250000")
    return {"amount": amount, "region": form.get("region", "north")}

class ClaimRecord:
    def __init__(self, policy_holder: str, amount: float) -> None:
        if not 0 < amount <= 250_000:
            raise ValueError(f"invalid claim amount {amount}")
        self.policy_holder = policy_holder
        self.amount = amount

def payout(amount: float, deductible: float, approved: bool, fraud_flag: bool, limit: float) -> float:
    result = 0.0
    if approved:
        if not fraud_flag:
            if amount > deductible:
                if amount - deductible > limit:
                    result = limit
                else:
                    result = amount - deductible
    return result

class SmtpClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def send(self, to: str, body: str) -> str:
        return f"{self.host}:{self.port} -> {to}: {body}"

class ClaimReminder:
    def __init__(self) -> None:
        self.smtp = SmtpClient("smtp.insurer.test", 587)

    def remind(self, email: str, opened_on: date) -> str | None:
        days_open = (datetime.now().date() - opened_on).days
        if days_open < 14:
            return None
        return self.smtp.send(email, f"Your claim has been open for {days_open} days")

MAX_PHOTOS_PER_CLAIM = 10
REVIEW_SLA_DAYS = 10

@dataclass(frozen=True)
class Period:
    start: date
    end: date

    def days(self) -> int:
        return (self.end - self.start).days

    def contains(self, d: date) -> bool:
        return self.start <= d <= self.end

    def overlaps(self, other: Period) -> bool:
        return self.start <= other.end and other.start <= self.end

    def intersect(self, other: Period) -> Period | None:
        return Period(max(self.start, other.start), min(self.end, other.end)) if self.overlaps(other) else None

    def __str__(self) -> str:
        return f"{self.start.isoformat()}..{self.end.isoformat()}"

class Notifier(Protocol):
    def notify(self, to: str, text: str) -> str: ...

class EmailNotifier(Notifier):
    def notify(self, to: str, text: str) -> str:
        return f"email {to}: {text}"

class SmsNotifier(Notifier):
    def notify(self, to: str, text: str) -> str:
        return f"sms {to}: {text[:160]}"

def notify_holder(notifiers: list[Notifier], to: str, text: str) -> list[str]:
    return [n.notify(to, text) for n in notifiers]
