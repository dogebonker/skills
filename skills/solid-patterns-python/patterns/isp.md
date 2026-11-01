# Interface Segregation (ISP)

A client should depend only on the methods it actually calls.

Refs: https://cs.utexas.edu/~downing/papers/ISP-1996.pdf
Example: [examples/isp.py](../examples/isp.py)

**Principle** — Martin calls interfaces that serve several kinds of clients "fat" and shows that they couple those clients to each other. In Python the fat interface is usually an ABC used as a parameter type, or a concrete class. `typing.Protocol` (PEP 544) fixes it cheaply: the consumer declares the slice it uses, and any object with those methods satisfies it implicitly, with no base class, as in Go.

**Violation signals** — A function annotated with a wide ABC or concrete class (`welcome_message_v1(repo: CustomerRepository)`) that calls one method. Test doubles that subclass the ABC and stub methods with `raise AssertionError` (`FatFake`). Implementations that raise `NotImplementedError` for half the ABC.

**Fix** — Declare `EmailLookup(Protocol)` with only `find_email`, next to the consumer, and annotate `welcome_message(repo: EmailLookup, ...)`. `InMemoryCustomerRepository` still fits without changes, and the test double `EmailFake` is one method with no base class. If the client needs a single callable, `Callable[[str], str | None]` is narrower still.

**When not to apply** — Do not define a protocol per method for every class, or split an interface that each client uses whole. Without a type checker in CI, protocols are documentation only; then a docstring may carry the contract.

**Related** — **Adapter** (`gof-patterns-python/patterns/adapter.md`) to expose a narrow view of a wide object; **Facade** (`gof-patterns-python/patterns/facade.md`); **SRP** ([srp.md](srp.md)); **DIP** ([dip.md](dip.md)), whose ports should be this small; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
