# Prototype

Derive or implement `Clone`; a clone of owned data is already an independent deep copy.

Refs: https://refactoring.guru/design-patterns/prototype/rust/example
Example: [examples/prototype.rs](../examples/prototype.rs)

**Intent** — Create new values by cloning an existing, pre-configured one instead of rebuilding it.

**Problem** — Building an invoice template means loading terms, lines and metadata. Repeating that for every customer is slow and duplicates setup code.

**Applicability** — **Use** when objects are costly to build and differ only slightly, or you need copies without knowing the concrete type. **Avoid** a `Prototype` trait for plain data: `#[derive(Clone)]` is the entire pattern.

**Rust implementation** — `#[derive(Clone)]` on `InvoiceTemplate` gives a deep copy because `String`, `Vec` and `HashMap` own their data. Mutating the copy never touches the original. For trait objects, `Box<dyn Shape>` cannot derive `Clone`, so add `fn clone_box(&self) -> Box<dyn Shape>` to the trait and implement `Clone for Box<dyn Shape>` through it. The gotcha: `Rc` and `Arc` fields clone the pointer, not the data, so a copy still shares state. Call `Rc::make_mut` or clone the inner value when you need independence.

**Consequences** — Cheap, readable copies with no extra API. The cost is that every field must be `Clone`, and trait objects need the `clone_box` workaround.

**Related patterns** — **Memento** stores a copy to restore later; **Flyweight** shares data instead of copying it; **Builder** constructs from scratch instead.
