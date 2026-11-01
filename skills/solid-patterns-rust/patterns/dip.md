# Dependency Inversion (DIP)

High-level policy should not depend on low-level details; both depend on an abstraction that the policy owns.

Refs: https://cs.utexas.edu/~downing/papers/DIP-1996.pdf, https://doc.rust-lang.org/book/ch18-02-trait-objects.html
Example: [examples/dip.rs](../examples/dip.rs)

**Principle** — In Martin's paper a copy routine is welded to a keyboard and a printer until both depend on abstract reader and writer types. In Rust the abstraction is a trait declared in the policy module or crate, implemented by the detail crate. Inject it as a generic parameter (`ReorderPolicy<S: Supplier>`, static dispatch, zero cost) or as `Box<dyn Supplier>` when the choice is made at runtime or the type must not leak into signatures.

**Violation signals** — A business struct with a concrete client field (`supplier: HttpSupplier`) built inside `new()`, as `policy_v1` does. Domain crates depending on `reqwest`, `sqlx` or an SDK in `Cargo.toml`. Tests that need a network or database because the policy names its detail.

**Fix** — Put `trait Supplier` in `policy`, make `ReorderPolicy` generic over it, and implement the trait for `HttpSupplier` on the detail side. `main` picks the concrete type.

**When not to apply** — A trait and a type parameter for every collaborator with one implementation spreads generics through every signature. Stable `std` types (`Vec`, `String`, `Duration`) need no abstraction. Start concrete; invert when a second implementation or a crate boundary appears.

**Related** — **Adapter** (`gof-patterns-rust/patterns/adapter.md`) for the impl that fits the client to the trait; **Factory Method** (`gof-patterns-rust/patterns/factory-method.md`) for choosing the detail at runtime; **ISP** ([isp.md](isp.md)) to keep the owned trait small; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
