# Liskov Substitution (LSP)

Every implementation of a trait must keep the trait's documented contract, so code written against the trait works with any of them.

Refs: https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf, https://doc.rust-lang.org/std/hash/trait.Hash.html
Example: [examples/lsp.rs](../examples/lsp.rs)

**Principle** — Liskov and Wing: a subtype must accept at least what its supertype accepts and guarantee at least what it guarantees. Rust has no inheritance, so LSP is about trait contracts, which the type checker does not verify. Standard-library traits state laws in their docs: `Hash` must agree with `Eq`, `Ord` must be a total order. Breaking a law is a logic error, not undefined behavior, so it compiles and fails quietly.

**Violation signals** — Hand-written `PartialEq` beside `#[derive(Hash)]`, as `SkuV1` has; clippy's deny-by-default `derived_hash_with_manual_eq` lint flags it. Trait methods whose body is `unimplemented!()`, `todo!()` or `panic!`. Impls returning `Err(Unsupported)`. Callers avoiding a trait-based API (`HashSet`, `sort`) and writing a workaround like `unique_count_v1`.

**Fix** — Make the contract hold by construction. `Sku::new` normalises case once, then `PartialEq`, `Eq` and `Hash` are all derived from the same field. Where an impl cannot honor a method, split the trait so the type implements only what it supports.

**When not to apply** — Traits that document an optional capability (`Iterator` may or may not be fused; `FusedIterator` promises more) are not violated by the weaker impl. Do not invent laws the trait never stated.

**Related** — **Decorator** (`gof-patterns-rust/patterns/decorator.md`) and **Proxy** (`gof-patterns-rust/patterns/proxy.md`) must keep the wrapped contract; **Adapter** (`gof-patterns-rust/patterns/adapter.md`) for a newtype with its own impls; **ISP** ([isp.md](isp.md)) for splitting a trait.
