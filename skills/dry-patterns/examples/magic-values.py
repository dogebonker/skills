"""Magic values: unexplained literals become named constants and enums."""
from __future__ import annotations

from enum import IntEnum

# --- Violation ---
def shipping_cents_v1(subtotal_cents: int, status: int) -> int:
    if status == 3:
        return 0
    if subtotal_cents >= 5000:
        return 0
    return 499


def reminder_delay_v1() -> int:
    return 259200


# --- Fix ---
class OrderStatus(IntEnum):
    PENDING = 1
    PAID = 2
    CANCELLED = 3


FREE_SHIPPING_THRESHOLD_CENTS = 50_00
STANDARD_SHIPPING_CENTS = 4_99
SECONDS_PER_DAY = 24 * 60 * 60
PAYMENT_REMINDER_DAYS = 3


def shipping_cents(subtotal_cents: int, status: OrderStatus) -> int:
    if status is OrderStatus.CANCELLED:
        return 0
    if subtotal_cents >= FREE_SHIPPING_THRESHOLD_CENTS:
        return 0
    return STANDARD_SHIPPING_CENTS


def reminder_delay() -> int:
    return PAYMENT_REMINDER_DAYS * SECONDS_PER_DAY


if __name__ == "__main__":
    for subtotal, status in ((1200, OrderStatus.PAID), (7500, OrderStatus.PAID), (1200, OrderStatus.CANCELLED)):
        before = shipping_cents_v1(subtotal, int(status))
        after = shipping_cents(subtotal, status)
        print(subtotal, status.name, after, "same" if before == after else "DIFFERENT")
    print("reminder", reminder_delay(), "same" if reminder_delay_v1() == reminder_delay() else "DIFFERENT")
