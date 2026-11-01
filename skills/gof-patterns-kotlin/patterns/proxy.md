# Proxy

A stand-in implements the same interface, delegates the rest with `by`, and controls access with caching, laziness or checks.

Refs: https://refactoring.guru/design-patterns/proxy/java/example
Example: [examples/proxy.kt](../examples/proxy.kt)

**Intent** — Control access to an object by placing a substitute with the same interface in front of it.

**Problem** — Network forecasts are slow, and calling them repeatedly for the same city wastes time and data.

**Applicability** — **Use** when you need caching, lazy creation, access checks, logging or remote access without changing the real class or its callers. **Avoid** a proxy class when only lazy initialisation is needed: a property delegate such as `val real by lazy { RemoteWeather() }` is enough.

**Kotlin implementation** — `CachingWeather(real: Weather) : Weather by real` forwards `units()` untouched and overrides `forecast` with `getOrPut`. Callers hold a `Weather` and cannot tell. The code is the same shape as Decorator, and the difference is intent: a proxy controls access, a decorator adds features. Retrofit builds a runtime proxy for your API interface, and `by lazy` and `Delegates` are language-level proxies. Gotcha: cache invalidation and thread safety are your job here, and a plain `mutableMapOf` is not safe across threads.

**Consequences** — Transparent control and no change to the real object. An extra layer can hide latency or stale data.

**Related patterns** — **Decorator** adds behaviour instead of controlling access; **Adapter** changes the interface; **Facade** offers a new simpler interface.
