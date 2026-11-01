"""OCP: add a payment method without editing the fee calculation. Both versions agree."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Mapping


@dataclass(frozen=True)
class Payment:
    method: str
    amount_cents: int


# --- Violation: every new payment method is another edit to this chain.
def fee_cents_v1(p: Payment) -> int:
    if p.method == "card":
        return round(p.amount_cents * 0.029) + 30
    elif p.method == "bank":
        return 50
    elif p.method == "wallet":
        return round(p.amount_cents * 0.015)
    raise ValueError(f"unknown payment method: {p.method}")


# --- Fix: fee rules are a mapping of callables; fee_cents stays closed, the table is open.
FeeRule = Callable[[int], int]

DEFAULT_FEE_RULES: Mapping[str, FeeRule] = MappingProxyType({
    "card": lambda cents: round(cents * 0.029) + 30,
    "bank": lambda cents: 50,
    "wallet": lambda cents: round(cents * 0.015),
})


def fee_cents(p: Payment, rules: Mapping[str, FeeRule] = DEFAULT_FEE_RULES) -> int:
    rule = rules.get(p.method)
    if rule is None:
        raise ValueError(f"unknown payment method: {p.method}")
    return rule(p.amount_cents)


if __name__ == "__main__":
    for method in ("card", "bank", "wallet"):
        p = Payment(method, 12000)
        print(method, "violation:", fee_cents_v1(p), "fix:", fee_cents(p), "same output:", fee_cents_v1(p) == fee_cents(p))
    # Extension: a new method is a new entry passed in by the caller. fee_cents is untouched.
    with_voucher = {**DEFAULT_FEE_RULES, "voucher": lambda cents: 0}
    print("voucher fix:", fee_cents(Payment("voucher", 12000), with_voucher))
