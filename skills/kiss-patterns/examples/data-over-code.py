"""Data over code: a branch ladder that only maps keys to values becomes a table."""
from __future__ import annotations


# --- Violation ---
def shipping_cents_v1(country: str) -> int:
    if country == "PT":
        return 399
    elif country == "ES":
        return 599
    elif country == "FR":
        return 799
    elif country == "DE":
        return 799
    elif country == "NL":
        return 899
    else:
        return 1499


# --- Fix: the knowledge is a table; the logic is one lookup ---
SHIPPING_CENTS = {"PT": 399, "ES": 599, "FR": 799, "DE": 799, "NL": 899}
DEFAULT_SHIPPING_CENTS = 1499


def shipping_cents(country: str) -> int:
    return SHIPPING_CENTS.get(country, DEFAULT_SHIPPING_CENTS)


if __name__ == "__main__":
    for country in ("PT", "DE", "NL", "US"):
        before, after = shipping_cents_v1(country), shipping_cents(country)
        print(country, after, "same" if before == after else "DIFFERENT")
