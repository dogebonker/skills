# Smallest Thing That Works

Start with the simplest code that passes the tests, then refine it by Beck's rules of simple design.

Refs: https://martinfowler.com/bliki/BeckDesignRules.html
Example: [examples/smallest-thing-that-works.py](../examples/smallest-thing-that-works.py)

**Principle** — Kent Beck's four rules, in priority order as Fowler states them: passes the tests, reveals intention, no duplication, fewest elements. Fowler treats the middle two as refining each other. Anything that serves none of the first three goes. Ward Cunningham recalls asking Beck "what's the simplest thing that could possibly work?" when they were stuck, to get something concrete running and refine from there (https://www.artima.com/articles/the-simplest-thing-that-could-possibly-work). Rich Hickey's "Simple Made Easy" adds that simple (one concern, not intertwined) is not the same as easy (familiar).

**Violation signals** — Classes, caches and configuration around a one-line question (`LeapYearCalculator` with a `calendar_system` and a `_cache`). Hand-written logic the standard library already provides. Code written for inputs no test or caller supplies.

**Fix** — Check whether the stdlib or platform already does it, then write the minimum that passes the tests. `is_leap_year()` is `calendar.isleap(year)`. Grow the design when a new test demands it.

**When not to apply** — "Simplest" is not "first thing typed". Skipping validation at trust boundaries, error handling that prevents data loss, or security checks is not simple, it is incomplete. A shortcut that complects concerns is easy, not simple.

**Related** — **Facade** (`gof-patterns-typescript/patterns/facade.md`) when the library call already hides the subsystem; [`yagni`](yagni.md); [`delete-before-adding`](delete-before-adding.md); [`knowledge-not-text`](../../dry-patterns/patterns/knowledge-not-text.md) for the no-duplication rule.
