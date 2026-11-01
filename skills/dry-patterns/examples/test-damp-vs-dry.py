"""Tests favour DAMP (descriptive and meaningful phrases) over DRY: each test
states the input that matters; a defaults-plus-overrides factory removes the rest."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Callable


@dataclass(frozen=True)
class Order:
    subtotal_cents: int
    loyalty_years: int
    coupon: str | None


def discount_cents(order: Order) -> int:
    if order.coupon == "WELCOME10":
        return order.subtotal_cents // 10
    if order.loyalty_years >= 5:
        return order.subtotal_cents // 20
    return 0


# --- Violation: one generic table runner; a failure says "case 2", and the
# meaning of each row is hidden in positional fields and flags ---
CASES: list[tuple[Any, ...]] = [
    (10000, 0, None, 0, False),
    (10000, 0, "WELCOME10", 1000, False),
    (10000, 6, None, 500, False),
    (10000, 6, "WELCOME10", 1000, True),
]


def run_table_tests() -> int:
    passed = 0
    for i, (sub, years, coupon, expected, coupon_wins) in enumerate(CASES):
        got = discount_cents(Order(sub, years, coupon))
        assert got == expected, f"case {i}"
        if coupon_wins:
            assert got == sub // 10, f"case {i} precedence"
        passed += 1
    return passed


# --- Fix: a factory with defaults, and one named test per behaviour ---
def make_order(**overrides: Any) -> Order:
    return replace(Order(subtotal_cents=10000, loyalty_years=0, coupon=None), **overrides)


def test_no_discount_for_new_customer_without_coupon() -> None:
    assert discount_cents(make_order()) == 0


def test_welcome_coupon_takes_ten_percent() -> None:
    assert discount_cents(make_order(coupon="WELCOME10")) == 1000


def test_five_year_customer_gets_five_percent() -> None:
    assert discount_cents(make_order(loyalty_years=6)) == 500


def test_coupon_beats_loyalty_discount() -> None:
    assert discount_cents(make_order(loyalty_years=6, coupon="WELCOME10")) == 1000


DAMP_TESTS: list[Callable[[], None]] = [
    test_no_discount_for_new_customer_without_coupon,
    test_welcome_coupon_takes_ten_percent,
    test_five_year_customer_gets_five_percent,
    test_coupon_beats_loyalty_discount,
]

if __name__ == "__main__":
    dry_passed = run_table_tests()
    for test in DAMP_TESTS:
        test()
        print("passed", test.__name__)
    print(f"table runner: {dry_passed} passed, DAMP tests: {len(DAMP_TESTS)} passed")
