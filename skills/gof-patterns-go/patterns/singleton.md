# Singleton

A package-level value created once with `sync.Once`.

Refs: https://refactoring.guru/design-patterns/singleton/go/example
Example: [examples/singleton.go](../examples/singleton.go)

**Intent** — Guarantee a single instance with a global access point.

**Problem** — Two parts of the program must share one connection pool or config, and creating it twice would be wrong or costly.

**Applicability** — **Use** when initialization is expensive, must run at most once, and is genuinely needed process-wide. **Avoid** a lazy singleton accessor when a package-level `var` or a value built in `main` and passed in will do: both are simpler and easier to test than a hidden global.

**Go implementation** — Use `sync.Once` with `once.Do(func(){...})` inside a `Get()` function, as in the example, or `sync.OnceValue` for a typed one-liner. `sync.Once` is goroutine safe, so no manual double-checked locking. Most Go programs do better with package-level vars or injecting the dependency, because singletons hide dependencies and make tests share state. Gotcha: a panic inside `Do` still counts as done; use `OnceValues` if init can fail and return the error; the error is cached too, so a failed init is never retried, and a mutex-guarded lazy init is the fix when retry matters.

**Consequences** — One initialization with safe concurrent access. The cost is hidden global state, harder tests, and lifetime tied to the process.

**Related patterns** — **Abstract Factory** has concrete factories that are often created once; **Flyweight** shares many instances rather than one.
