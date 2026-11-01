"""Premature optimization: clever speed-ups in code nobody measured. Write the
clear version, profile, then optimize the hot spot the profile names."""
from __future__ import annotations

import cProfile
import io
import pstats
from typing import NamedTuple


class Order(NamedTuple):
    order_id: int
    total_cents: int

# --- Violation: a hand-unrolled loop and an identity-keyed cache for a report run once a day ---
_cache: dict[int, int] = {}


def average_order_cents_v1(orders: list[Order]) -> int:
    key = id(orders)  # stale if the list is mutated or its id is reused
    if key in _cache:
        return _cache[key]
    total, i, n = 0, 0, len(orders)
    while i + 4 <= n:
        total += orders[i][1] + orders[i + 1][1] + orders[i + 2][1] + orders[i + 3][1]
        i += 4
    while i < n:
        total += orders[i][1]
        i += 1
    result = total // n if n else 0
    _cache[key] = result
    return result


# --- Fix: the obvious version ---
def average_order_cents(orders: list[Order]) -> int:
    if not orders:
        return 0
    return sum(o.total_cents for o in orders) // len(orders)


if __name__ == "__main__":
    for orders in ([], [Order(1, 1200)], [Order(i, 1000 + i * 37) for i in range(1, 11)]):
        before, after = average_order_cents_v1(orders), average_order_cents(orders)
        print(len(orders), after, "same" if before == after else "DIFFERENT")

    # Measure before optimizing: the profile shows where time goes.
    big = [Order(i, i % 9000) for i in range(200_000)]
    profiler = cProfile.Profile()
    profiler.runcall(average_order_cents, big)
    out = io.StringIO()
    pstats.Stats(profiler, stream=out).sort_stats("cumulative").print_stats(3)
    print("profiled", sum(1 for line in out.getvalue().splitlines() if "average_order_cents" in line), "hot function")
