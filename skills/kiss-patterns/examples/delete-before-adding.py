"""Delete before adding: remove the dead payment branches and flag first,
then add the new gift card method to a smaller function."""
from __future__ import annotations

LEGACY_CHEQUES_ENABLED = False  # switched off in 2019, never removed


# --- Violation: the new branch is added on top of dead code ---
def checkout_fee_cents_v1(method: str, amount_cents: int) -> int:
    if method == "card":
        return 25 + amount_cents * 14 // 1000
    if method == "cheque":
        if LEGACY_CHEQUES_ENABLED:
            return 150
        raise ValueError("cheques are not accepted")
    if method == "fax_order":  # no client can send this any more
        return 300
    if method == "mbway":
        return 10
    if method == "gift_card":  # the new feature
        return 0
    raise ValueError(f"unknown method {method}")


# --- Fix: delete the dead branches and the flag, then add the feature ---
def checkout_fee_cents(method: str, amount_cents: int) -> int:
    if method == "card":
        return 25 + amount_cents * 14 // 1000
    if method == "mbway":
        return 10
    if method == "gift_card":
        return 0
    raise ValueError(f"unknown method {method}")


if __name__ == "__main__":
    for method in ("card", "mbway", "gift_card"):
        before, after = checkout_fee_cents_v1(method, 4500), checkout_fee_cents(method, 4500)
        print(method, after, "same" if before == after else "DIFFERENT")
    for method in ("cheque", "bitcoin"):
        for fn in (checkout_fee_cents_v1, checkout_fee_cents):
            try:
                fn(method, 4500)
            except ValueError:
                pass
            else:
                raise AssertionError(method)
        print(method, "rejected by both")
    # The one deliberate change: the dead fax_order branch is deleted, so it is now rejected.
    print("fax_order", checkout_fee_cents_v1("fax_order", 4500), "-> rejected now (dropped on purpose)")
