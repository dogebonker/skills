# Abstract Factory

A factory object exposes several creation methods that return products guaranteed to belong to the same family.

Refs: https://refactoring.guru/design-patterns/abstract-factory/python/example
Example: [examples/abstract-factory.py](../examples/abstract-factory.py)

**Intent** — Create related objects (connection and SQL dialect, widgets in one theme) without naming their concrete classes.

**Problem** — Mixing a Postgres connection with a MySQL quoting rule produces broken queries. Code needs a way to obtain a consistent set.

**Applicability** — **Use** when two or more products must vary together and the client should be unaware of which family it has. **Avoid** an Abstract Factory class family when only one product varies (use Factory Method or a function), or when a module of functions per backend, selected once at import, is enough.

**Python implementation** — Declare `DbFactory`, `Connection` and `Dialect` as Protocols; no inheritance is needed, structural typing is enough. `PgFactory` and `MySqlFactory` each return their own matching products. Client code such as `select_orders(factory)` takes the factory as a parameter. Pick the factory once at startup, for example from config, and pass it down. Gotcha: do not create a second factory mid-flow, or the family guarantee is lost.

**Consequences** — Families stay consistent and swapping is one line. Cost: adding a new product type to the family touches every factory.

**Related patterns** — **Factory Method** is how each factory method is often written; **Singleton** for the single chosen factory (a module global is enough); **Facade** suffices when you only want a simpler entry point.
