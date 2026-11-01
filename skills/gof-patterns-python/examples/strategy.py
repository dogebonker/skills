"""Strategy: interchangeable algorithms are just functions."""
from __future__ import annotations

from typing import Callable

Pricing = Callable[[float], float]


def regular(total: float) -> float:
    return total


def black_friday(total: float) -> float:
    return total * 0.7


def loyalty(total: float) -> float:
    return max(total - 10, 0)


STRATEGIES: dict[str, Pricing] = {
    "regular": regular,
    "black_friday": black_friday,
    "loyalty": loyalty,
}


def checkout(total: float, pricing: Pricing = regular) -> float:
    return round(pricing(total), 2)


if __name__ == "__main__":
    for name, fn in STRATEGIES.items():
        print(name, checkout(100.0, fn))
    print(checkout(50.0, lambda t: t * 0.9))
