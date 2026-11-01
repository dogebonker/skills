# Premature Optimization

Write the clear version first, measure, and optimize only the code the measurement shows is critical.

Refs: https://doi.org/10.1145/356635.356640
Example: [examples/premature-optimization.py](../examples/premature-optimization.py)

**Principle** — Knuth's "Structured Programming with go to Statements" (ACM Computing Surveys, 1974) is the source of "premature optimization is the root of all evil". In context he warns against worrying about small efficiencies in noncritical code most of the time ("say about 97%"), because it hurts debugging and maintenance, and in the same passage says not to pass up the critical 3%, found by measurement, since intuitive guesses about bottlenecks are often wrong. (Context confirmed via a secondary summary, https://www.embeddedrelated.com/showarticle/1044.php; the original scan was not read.)

**Violation signals** — Manual loop unrolling, bit tricks or hand-rolled caches in code with no profile or benchmark behind them (`average_order_cents_v1` with an `id()`-keyed cache). Caches with no invalidation. Readability traded for speed in code that runs once a day.

**Fix** — Write `average_order_cents()` with `sum()` and `len()`. Profile with `cProfile` (Python) or `node --cpu-prof`, find the hot spot, change it, and measure again. Keep the benchmark with the change.

**When not to apply** — Choosing a sensible algorithm and data structure up front is design, not premature optimization: avoid O(n²) scans over unbounded data, N+1 queries and blocking I/O on hot paths. Hard latency budgets justify early measurement.

**Related** — **Flyweight** (`gof-patterns-typescript/patterns/flyweight.md`) and **Proxy** (`gof-patterns-typescript/patterns/proxy.md`) for memory and caching once measured; [`smallest-thing-that-works`](smallest-thing-that-works.md); [`data-normalization`](../../dry-patterns/patterns/data-normalization.md) before denormalizing for speed.
