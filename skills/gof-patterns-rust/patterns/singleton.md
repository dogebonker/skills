# Singleton

A `static` holding a `OnceLock` (or `LazyLock`) initialised on first access, with a `Mutex` or atomics inside for mutation.

Refs: https://refactoring.guru/design-patterns/singleton/rust/example
Example: [examples/singleton.rs](../examples/singleton.rs)

**Intent** — Provide one global instance that is created on first use and safe to share between threads.

**Problem** — Configuration or a connection pool must exist once, and passing it through every function is awkward.

**Applicability** — **Use** when a process-wide resource truly has one instance, such as parsed config, a regex table or a logger handle. **Avoid** a global when the value can be passed as a parameter or held in a struct: explicit dependencies are easier to test. When a global is right, `LazyLock<T>` replaces hand-written `OnceLock` plus an accessor.

**Rust implementation** — Use `static INSTANCE: OnceLock<Config> = OnceLock::new();` inside `fn config() -> &'static Config` and call `get_or_init`. The initialiser runs once even under contention. For mutable state put `Mutex` or atomics inside the struct, because a `static` can only give out shared references. Avoid `static mut`, which is unsafe and unnecessary. The gotcha: statics are never dropped, so types needing cleanup should not live there, and tests share them across cases.

**Consequences** — Thread-safe lazy initialisation with no unsafe code. The cost is hidden global state and harder testing.

**Related patterns** — **Abstract Factory** is often exposed as a singleton; **Facade** is commonly one shared instance; **Flyweight** for many shared instances rather than one.
