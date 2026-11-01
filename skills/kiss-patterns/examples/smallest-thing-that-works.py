"""Smallest thing that works: Beck's rules in order. Passes the tests, reveals
intention, no duplication, fewest elements. Here the fewest elements is a stdlib call."""
from __future__ import annotations

import calendar


# --- Violation: a configurable calculator with a cache, for one boolean question ---
class LeapYearCalculator:
    def __init__(self, calendar_system: str = "gregorian") -> None:
        self.calendar_system = calendar_system
        self._cache: dict[int, bool] = {}

    def is_leap(self, year: int) -> bool:
        if year in self._cache:
            return self._cache[year]
        if self.calendar_system == "gregorian":
            result = False
            if year % 4 == 0:
                result = True
                if year % 100 == 0:
                    result = year % 400 == 0
        else:
            raise ValueError(self.calendar_system)
        self._cache[year] = result
        return result


# --- Fix ---
def is_leap_year(year: int) -> bool:
    return calendar.isleap(year)


if __name__ == "__main__":
    calc = LeapYearCalculator()
    years = range(1800, 2401)
    assert all(calc.is_leap(y) == is_leap_year(y) for y in years)
    sample = [1900, 2000, 2024, 2100]
    print({y: is_leap_year(y) for y in sample}, f"same for {len(years)} years")
