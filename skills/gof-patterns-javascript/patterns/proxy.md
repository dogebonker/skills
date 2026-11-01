# Proxy

Controls access to an object by intercepting calls, reads, and writes; useful for lazy initialization, caching, and security; can be implemented via GoF or native JavaScript Proxy.

Refs: https://github.com/HowProgrammingWorks/Proxy  
Example: [examples/proxy.js](../examples/proxy.js) (`PriceApiProxy`, `StatReadStream`)

**Intent** — Stand in for an object with the same interface and control access to it (cache, stats, policy) without changing its callers.

**Problem** — Observability, caching, or safety should sit at a stable choke point.

**Applicability** — **Use** when calls to a target need caching, stats, lazy creation or access checks at one choke point. **Avoid** the built-in `Proxy` on hot paths or where types matter: a class that holds the target and exposes the same methods is enough. The built-in fits when you must intercept arbitrary property access.

**JS implementation** — `PriceApiProxy` holds a `PriceApi`, exposes the same `fetch`, and adds a cache and hit/miss stats. When callers need the platform type itself (a stream passed to `pipe`), extend it and forward to `super`, keeping its return values (`emit` returns a boolean), as `StatReadStream` does. Gotcha: a string chunk's `length` counts UTF-16 units, not bytes, so `StatReadStream` counts with `Buffer.byteLength`.

**Consequences** — Centralized behavior; subclassing platform types ties you to their upgrade semantics.

**Related patterns** — **Wrapper** for the lighter function-level case; **Decorator** adds behavior in stackable layers, while a proxy controls access.
