# Proxy

A stand-in with the same protocol as a real object that controls access, adding laziness, caching, or checks.

Refs: https://refactoring.guru/design-patterns/proxy/swift/example
Example: [examples/proxy.swift](../examples/proxy.swift)

**Intent** — Provide a substitute that controls access to another object while presenting the same interface.

**Problem** — Loading from disk or the network is slow, and repeated requests should hit a cache.

**Applicability** — **Use** when you need lazy creation, caching, access control, or logging in front of a real service without changing callers. **Avoid** a proxy type when the laziness or caching belongs inside one type: `lazy var`, a cache dictionary in the type, or a property wrapper is enough.

**Swift implementation** — Write the proxy as a generic `final class` over the protocol (`CachingImageProxy<Real: ImageLoader>`) that forwards to `real` and stores results, as the example does. Hold the cache in a class or actor proxy so the protocol stays unchanged; use an actor when tasks share the proxy. For remote services make the proxy `async`. Keep the proxy's type signature identical to the real one.

**Consequences** — Transparent control and no change to clients. One more indirection and a possible latency or staleness bug.

**Related patterns** — **Decorator** adds features while Proxy controls access; **Adapter** changes the interface; **Facade** wraps many objects; **Flyweight** shares instances.
