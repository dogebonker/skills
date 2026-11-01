# Adapter

Converts an incompatible interface into a compatible one, enabling third-party component usage without altering its code; can even transform a function contract into an object or vice versa.

Refs: https://github.com/HowProgrammingWorks/Adapter  
Example: [examples/adapter.js](../examples/adapter.js)

**Intent** — Make something you cannot change speak the protocol your code expects (sync->async, callback->Promise, array->queue).

**Problem** — Vendor API, legacy callback, or shape mismatch blocks composition without rewriting upstream.

**Applicability** — **Use** at boundaries (infra, old modules). **Avoid** an adapter class when the mismatch is a single call: a one-line wrapper at the import site is enough.

**JS implementation** — Higher-order `promisify` turns a callback API into promises; `ArrayToQueueAdapter` delegates to an array behind a queue interface and keeps a head index, so `dequeue` is O(1) amortized. Iterator and async-iterator adapters (`[Symbol.asyncIterator]` over events or timers) are common. Gotcha: `Array.prototype.shift` is O(n), so a queue built on it slows down as it grows.

**Consequences** — Isolation of ugliness; a thin layer can still leak if error shapes differ—normalize them deliberately.

**Related patterns** — **Wrapper** adds behavior around the same interface; **Facade** simplifies many adapters behind one face.
