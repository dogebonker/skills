# Proxy

An object with the same interface as a real service that sits in front of it to add lazy creation, caching, access control or logging.

Refs: https://refactoring.guru/design-patterns/proxy/typescript/example
Example: [examples/proxy.ts](../examples/proxy.ts)

**Intent** — Provide a stand-in that controls access to another object.

**Problem** — Loading an image is slow, and you want to defer it until first use and cache results without changing callers.

**Applicability** — **Use** when you need lazy init, caching, access checks, or remote access behind an unchanged interface. **Avoid** a proxy class when a memoizing wrapper function covers caching; a JavaScript `Proxy` object helps when you must intercept arbitrary property access, such as validation or change tracking.

**TypeScript implementation** — `CachingImageProxy implements ImageService`, creates `DiskImageService` on first call with `??=`, and keeps results in a `Map`. Callers hold the variable as `ImageService` and cannot tell. The built-in `new Proxy(target, handler)` is dynamic and loses some static typing, so prefer an explicit class for named behaviours. Gotcha: cached values go stale without an invalidation rule.

**Consequences** — Transparent control over a costly or protected resource. It adds a layer and latency on first call, and staleness if caching.

**Related patterns** — **Decorator** adds features, while a proxy manages access; **Adapter** changes the interface; **Facade** simplifies many objects.
