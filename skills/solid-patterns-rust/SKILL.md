---
name: solid-patterns-rust
description: "SOLID principles (SRP, OCP, LSP, ISP, DIP) in Rust, read through traits, enums and generics. Use when designing or refactoring Rust modules, traits or dependencies against SOLID, or when deciding between a trait, an enum, generics and `dyn`."
---

# SOLID in Rust

- Read SOLID through modules, traits and generics; Rust has no inheritance, so the class-centric wording translates rather than applies.
- Split responsibilities by module and `impl` block; plain data structs with behavior in the modules that own it are idiomatic.
- Choose the open axis on purpose: a trait is open to new types, an `enum` is open to new operations and gives exhaustive `match`.
- Treat a trait's documented laws as its contract (`Hash` agrees with `Eq`, `Ord` is total); the compiler checks signatures only, so LSP lives in docs and tests.
- Keep traits small and combine them with bounds (`impl Print + Scan`) or supertraits instead of one wide trait with stubbed methods.
- Declare the trait where the policy lives and implement it on the detail side; inject with generics first and `Box<dyn Trait>` when the type is chosen at runtime or must not leak.
- Prefer a closure parameter (`impl Fn(..)`) over a single-method trait when the dependency has no state or name worth keeping.
- Add a trait when a second implementation or a crate boundary exists; a trait with one impl is overhead.

## How to use

Pick the principle from the index, then read its pattern file and its example before designing, reviewing or refactoring. Each entry has `patterns/<id>.md` and `examples/<id>.rs`; the example shows the violation and the fix in one file and prints that both behave the same. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Every pattern file has a "When not to apply" section: check it before recommending a split, a trait or a type parameter.

## Principles
- **Single Responsibility** (`srp`): one `impl` block or module serves unrelated owners, or a `utils` module collects unrelated code.
- **Open/Closed** (`ocp`): a `match` on a string or code grows an arm with every feature, or you must choose between a trait and an enum.
- **Liskov Substitution** (`lsp`): a trait impl breaks the trait's documented laws, stubs a method, or forces callers to work around it.
- **Interface Segregation** (`isp`): a wide trait forces stub methods, or a function bounds on more than it calls.
- **Dependency Inversion** (`dip`): business code holds or builds a concrete client, database or SDK type.
