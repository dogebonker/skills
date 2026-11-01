"""DRY is about knowledge: one rule written two ways is duplication; two rules
that happen to share a value are not."""
from __future__ import annotations

# --- Violation ---
# The VAT rule is written twice in different text, so a rate change must find both.
def invoice_gross_v1(net_cents: int) -> int:
    return round(net_cents * 120 / 100)


def receipt_gross_v1(net_cents: int) -> int:
    return net_cents + round(net_cents * 20 / 100)


# Two unrelated limits were merged because both happened to be 99.
LIMIT = 99


def cart_quantity_ok_v1(qty: int) -> bool:
    return 1 <= qty <= LIMIT


def restock_batch_ok_v1(qty: int) -> bool:
    return 1 <= qty <= LIMIT


# --- Fix ---
# One owner for the VAT knowledge.
VAT_PERCENT = 20


def gross(net_cents: int) -> int:
    return net_cents + round(net_cents * VAT_PERCENT / 100)


invoice_gross = gross
receipt_gross = gross

# Separate knowledge stays separate, even with the same value today.
MAX_CART_QUANTITY = 99  # product decision: UI stepper limit
MAX_RESTOCK_BATCH = 99  # warehouse decision: pallet capacity


def cart_quantity_ok(qty: int) -> bool:
    return 1 <= qty <= MAX_CART_QUANTITY


def restock_batch_ok(qty: int) -> bool:
    return 1 <= qty <= MAX_RESTOCK_BATCH


if __name__ == "__main__":
    for net in (1000, 1999, 25000):
        before = (invoice_gross_v1(net), receipt_gross_v1(net))
        after = (invoice_gross(net), receipt_gross(net))
        print("gross", net, after, "same" if before == after else "DIFFERENT")
    for qty in (0, 1, 99, 100):
        before = (cart_quantity_ok_v1(qty), restock_batch_ok_v1(qty))
        after = (cart_quantity_ok(qty), restock_batch_ok(qty))
        print("limits", qty, after, "same" if before == after else "DIFFERENT")
