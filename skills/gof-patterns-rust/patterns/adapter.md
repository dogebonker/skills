# Adapter

A newtype wrapper that implements your trait by delegating to the foreign type, usually constructed through `From`/`Into`.

Refs: https://refactoring.guru/design-patterns/adapter/rust/example
Example: [examples/adapter.rs](../examples/adapter.rs)

**Intent** — Wrap a type you cannot change so it satisfies the trait the rest of the code uses.

**Problem** — A legacy bank client takes dollars as `f64` and returns `bool`, while your checkout code speaks `PaymentGateway` with cents and `Result`.

**Applicability** — **Use** when you must reuse a third-party or legacy type behind your own trait. **Avoid** a newtype adapter when you own the trait: implement it directly on the foreign type, or change the signature. The newtype is needed only when both trait and type are foreign (orphan rule).

**Rust implementation** — Define `struct LegacyBankAdapter(LegacyBank);`, implement `PaymentGateway` for it, and add `impl From<LegacyBank> for LegacyBankAdapter` so call sites write `bank.into()`. Callers take `&impl PaymentGateway`, which keeps dispatch static. Use `Box<dyn PaymentGateway>` only when adapters are mixed at runtime. The gotcha: the wrapper is required only when the target trait is also foreign (the orphan rule forbids `impl ForeignTrait for ForeignType`, e.g. `std::fmt::Write` for a vendor type); here `PaymentGateway` is local, and the wrapper isolates the unit conversion. Implement `Deref` only if you truly want the inner API exposed.

**Consequences** — Third-party code stays untouched and conversions are explicit. The cost is a thin wrapper type and some forwarding code.

**Related patterns** — **Decorator** adds behaviour while keeping the interface; **Facade** simplifies a whole subsystem, not one type; **Proxy** has the same interface as the wrapped object.
