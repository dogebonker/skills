# Proxy

A struct implementing the same interface as the real service and delegating to it after adding a check, cache or lazy load.

Refs: https://refactoring.guru/design-patterns/proxy/go/example
Example: [examples/proxy.go](../examples/proxy.go)

**Intent** — Provide a substitute that controls access to a real object while presenting the same interface.

**Problem** — Repeated network fetches for the same URL waste time, but callers should not know caching exists.

**Applicability** — **Use** when you need lazy creation, caching, access control, rate limiting or remote-call hiding behind an identical interface. **Avoid** a proxy type when the wrapping is generic or the check belongs in the real type: a decorator function or a check in the type is enough.

**Go implementation** — Define a small `Fetcher` interface, implement it on the real `httpFetcher` and on `cachingProxy`, which holds the real one and a mutex-guarded map of `sync.OnceValue` funcs keyed by URL, as in the example, so concurrent callers of one URL share a single real fetch. Callers receive the interface and cannot tell the difference. Always protect shared proxy state with a mutex or `sync.Map`; a plain check-then-fetch-then-store lets concurrent callers fetch the same key twice. The pattern is structurally identical to Decorator; choose the name by intent (control versus enrichment).

**Consequences** — Transparent control over access without touching callers. The cost is added latency per call and a second type to keep in sync with the interface.

**Related patterns** — **Decorator** adds behavior, not access control; **Adapter** changes the interface; **Facade** exposes a new simpler interface.
