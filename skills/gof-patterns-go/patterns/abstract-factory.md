# Abstract Factory

An interface with one constructor method per product, implemented once per family.

Refs: https://refactoring.guru/design-patterns/abstract-factory/go/example
Example: [examples/abstract-factory.go](../examples/abstract-factory.go)

**Intent** — Provide an interface for creating a family of related objects without naming their concrete types.

**Problem** — A charger from one payment vendor must be paired with the refunder from the same vendor; mixing them produces runtime failures.

**Applicability** — **Use** when two or more products vary together along one axis (vendor, platform, theme) and the client must never mix families. **Avoid** a factory interface per family when there is a single product (use Factory Method) or the family is just a struct of funcs: filling it in directly is enough.

**Go implementation** — Declare `PaymentFactory` with `NewCharger` and `NewRefunder`, one small implementation per vendor (`stripeFactory`, `adyenFactory`). Clients such as `checkout` accept the factory interface and never import vendor types. Keep product interfaces tiny and separate (`Charger`, `Refunder`) so consumers depend only on what they call. For two products, a struct of function fields can replace the factory interface and is easier to fake in tests.

**Consequences** — Families stay consistent and swapping a vendor is one argument. The cost is many small types, and adding a product to the family changes every factory.

**Related patterns** — **Factory Method** for a single product, since each factory method is often one; **Singleton** for concrete factories, which are usually created once.
