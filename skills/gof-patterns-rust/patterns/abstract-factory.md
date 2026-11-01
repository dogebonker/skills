# Abstract Factory

A trait with one associated type per product; each family is a unit struct implementing the trait.

Refs: https://refactoring.guru/design-patterns/abstract-factory/rust/example
Example: [examples/abstract-factory.rs](../examples/abstract-factory.rs)

**Intent** — Produce a set of related objects from one family without naming their concrete types, and make mixing families impossible.

**Problem** — An app needs a connection and a migration writer that both belong to Postgres, or both to SQLite. Creating them separately lets someone pair a Postgres connection with SQLite SQL.

**Applicability** — **Use** when products come in matching sets and callers must not mix sets. **Avoid** a factory trait with associated types when there is one product or the family is chosen once at startup: a Factory Method or an enum of structs is enough.

**Rust implementation** — Declare `trait DbFactory { type Conn: Connection; type Mig: Migration; ... }`. Each backend implements it with concrete associated types, and client code is generic: `fn bootstrap<F: DbFactory>(f: &F)`. The compiler monomorphises per family and proves that `Conn` and `Mig` come from the same factory, which the classic pattern can only promise. Runtime family selection needs boxed products instead. The gotcha: a trait with associated types cannot be used as `dyn DbFactory` without fixing them.

**Consequences** — Static guarantees that families match and zero runtime cost. The cost is more types and more code per family, and runtime selection needs extra work.

**Related patterns** — **Factory Method** is what each factory method of an abstract factory is; **Singleton** for factories that are often a single shared value; **Bridge** for separating abstraction from implementation.
