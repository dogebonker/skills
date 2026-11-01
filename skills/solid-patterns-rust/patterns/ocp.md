# Open/Closed (OCP)

Add new behavior by adding code, not by editing code that already works.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html, https://doc.rust-lang.org/book/ch18-02-trait-objects.html
Example: [examples/ocp.rs](../examples/ocp.rs)

**Principle** — A module should be extensible without being modified. Martin's 1996 paper adds that full closure is impossible, so choose the changes to close against. Rust makes the choice explicit: a trait is open to new types (any crate can implement it for its own types) but adding a method without a default body edits every impl; an `enum` is open to new operations (write another `match`) but adding a variant edits every `match`. Pick the axis that actually changes.

**Violation signals** — `match` on a `&str` or an integer code that gains an arm with each feature, as `fee_cents_v1` does. The same enum matched in many files where variants are added often.

**Fix** — Define a trait for the varying behavior (`PaymentMethod`) and make each variant a type (`Card`, `BankTransfer`). Use `Box<dyn PaymentMethod>` when the set is chosen at runtime or mixed, and a generic `impl PaymentMethod` when one type is known at compile time.

**When not to apply** — A closed set you own (order status, HTTP method) is better as an `enum`: exhaustive `match` turns every missed case into a compile error, which a trait cannot do. A trait with one impl and no outside implementers is ceremony.

**Related** — **Strategy** (`gof-patterns-rust/patterns/strategy.md`) for swapping one algorithm; **Visitor** (`gof-patterns-rust/patterns/visitor.md`) for the enum-and-match side; **Decorator** (`gof-patterns-rust/patterns/decorator.md`) for extending by wrapping; **DIP** ([dip.md](dip.md)) for who owns the trait; **YAGNI** (`kiss-patterns/patterns/yagni.md`) for unused extension points.
