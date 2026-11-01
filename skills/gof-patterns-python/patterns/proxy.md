# Proxy

A stand-in with the same interface controls access to the real object: lazy loading, permission checks, caching or logging.

Refs: https://refactoring.guru/design-patterns/proxy/python/example
Example: [examples/proxy.py](../examples/proxy.py)

**Intent** — Control access to another object without changing how clients use it.

**Problem** — Loading a large image is expensive and should happen only when it is first rendered, and only for permitted users.

**Applicability** — **Use** for lazy initialisation, access control, remote or caching stand-ins. **Avoid** a proxy class when `functools.cached_property` or `lru_cache` gives the same effect directly; for generic forwarding consider `__getattr__`, but explicit methods keep typing clear.

**Python implementation** — `LazyImageProxy` implements the `Image` Protocol, checks `_allowed`, creates `HighResImage` on first `render()` and caches it in `_real`. Gotcha: with `__getattr__` forwarding, dunder methods are looked up on the type and are not forwarded, so define them explicitly.

**Consequences** — Transparent control and deferred cost. Cost: extra indirection and a possible latency surprise on first use.

**Related patterns** — **Decorator** adds behavior and the client builds the stack, whereas Proxy usually manages the lifecycle itself; **Adapter** changes the interface; **Facade** simplifies a subsystem.
