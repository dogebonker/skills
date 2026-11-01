# Liskov Substitution (LSP)

Any object that claims a type, by inheritance or by protocol, must keep every promise callers rely on.

Refs: https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf
Example: [examples/lsp.py](../examples/lsp.py)

**Principle** — Liskov and Wing define a subtype by behaviour: it may accept more and promise more, it must keep the supertype's invariants, and it must not allow state changes the supertype forbids. Martin's 1996 paper (https://cs.utexas.edu/~downing/papers/LSP-1996.pdf) adds that raising where the base did not breaks clients that do not expect the exception. In Python it covers subclasses and duck-typed protocols alike. mypy flags overrides that narrow a parameter type or widen a return type, but it cannot see behaviour.

**Violation signals** — An override that raises `NotImplementedError` or `PermissionError` the base never raised (`FixedDepositAccountV1.withdraw`), or does nothing. Callers branching on `isinstance` to avoid one subclass. An override with fewer accepted arguments, or that returns `None` where the base returned a value.

**Fix** — Drop the inheritance and split the capability: the `Withdrawable` protocol requires `withdraw`, `CheckingAccount` has it and `FixedDeposit` does not. mypy rejects `pay_from(FixedDeposit(...))`. At runtime, `isinstance(a, Withdrawable)` with `@runtime_checkable` checks only that members exist, not their signatures.

**When not to apply** — Do not invent class hierarchies to have something to substitute. If two types share no contract, give them no common base; a `Union` and a `match` may be simpler than a set of capability protocols.

**Related** — **Template Method** (`gof-patterns-python/patterns/template-method.md`), whose subclasses must honour each step; **Adapter** (`gof-patterns-python/patterns/adapter.md`) to wrap instead of subclassing; **ISP** ([isp.md](isp.md)); **OCP** ([ocp.md](ocp.md)).
