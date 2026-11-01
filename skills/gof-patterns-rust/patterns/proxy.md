# Proxy

A wrapper implementing the same trait as the real service, adding lazy loading, caching or access checks.

Refs: https://refactoring.guru/design-patterns/proxy/rust/example
Example: [examples/proxy.rs](../examples/proxy.rs)

**Intent** — Put a stand-in with the same interface in front of an object to manage how it is reached.

**Problem** — A remote price lookup is slow and repeated for the same SKUs.

**Applicability** — **Use** when you need caching, lazy creation, access control or logging in front of a service without changing callers. **Avoid** a proxy type when the goal is lazy init or memoisation: `OnceCell`, `LazyLock` or a memoising function is enough.

**Rust implementation** — `CachingProxy<S: PriceService>` implements `PriceService` and holds the real service plus `RefCell<HashMap<..>>`. The trait method takes `&self`, so the cache needs interior mutability; use `Mutex` when shared across threads. The gotcha is runtime borrow panics: do not keep a `borrow()` alive across the call to the inner service, and release it before `borrow_mut()`, as the example does. Callers take `&impl PriceService`, so the proxy is invisible to them.

**Consequences** — Transparent control over access. The cost is another layer and, with caching, stale data to think about.

**Related patterns** — **Decorator** adds behaviour, where a proxy controls access; **Adapter** changes the interface; **Flyweight** shares objects, where a proxy fronts one.
