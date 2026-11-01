# Object Pool

Reuses pre-created objects to save resources during frequent creation and destruction.

Refs: https://github.com/HowProgrammingWorks/Pool  
Example: [examples/object-pool.js](../examples/object-pool.js)

**Intent** — Amortize allocation and teardown by lending instances from a fixed reservoir.

**Problem** — Short-lived heavy objects (buffers, parsers, workers) or GC pressure from churn.

**Applicability** — **Use** under sustained bursty load with resettable objects. **Avoid** a pool when objects are cheap or hard to reset: allocating new ones and letting the GC collect them is enough.

**Preconditions** — `release` must restore a valid blank slate; clients must not steal references after release.

**JS implementation** — A stack of free instances plus `factory` for growth. `acquire` takes one and records it in an in-use `Set`; `release` returns early unless it removes the object from that set, then resets it and keeps it while the free stack is below the size cap. Gotcha: without the in-use check, releasing the same object twice puts it on the free stack twice, and two later `acquire` calls hand out the same object.

**Consequences** — Predictable memory; risk of stale state if reset is incomplete; cap size to avoid hoarding.

**Related patterns** — **Flyweight** shares immutable data, while a pool lends mutable objects to one holder at a time.
