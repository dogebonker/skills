# Liskov Substitution (LSP)

Any value that claims a type must keep every promise callers of that type rely on.

Refs: https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf
Example: [examples/lsp.kt](../examples/lsp.kt)

**Principle** — Liskov and Wing define a subtype by behaviour: it may accept more and promise more, and it must keep the supertype's invariants. Martin's 1996 paper (https://cs.utexas.edu/~downing/papers/LSP-1996.pdf) adds that a subclass throwing where the base did not breaks clients that do not expect the exception. Kotlin classes and members are final by default (https://kotlinlang.org/docs/inheritance.html), so `open` marks every place a substitute can appear; the compiler checks signatures, never behaviour.

**Violation signals** — An override that throws `UnsupportedOperationException` or `NotImplementedError`, or does nothing (`FixedDepositAccountV1.withdraw`). Callers using `is` checks to avoid one subclass. A read-only `List` cast to `MutableList`. An `open` member called from an `init` block, which runs before the subclass is initialised.

**Fix** — Replace the `open` base with capability interfaces: `HasBalance` and `Withdrawable`. `CheckingAccount` implements `Withdrawable`, `FixedDeposit` only `HasBalance`, so `payFrom(FixedDeposit(...))` does not compile. `filterIsInstance<Withdrawable>()` picks payable sources from a mixed list.

**When not to apply** — Do not build interface lattices for types that share no contract. A sealed interface with an exhaustive `when` often models "some accounts can withdraw" more plainly than many small interfaces.

**Related** — **Template Method** (`gof-patterns-kotlin/patterns/template-method.md`), whose `open` steps every subclass must honour; **Decorator** (`gof-patterns-kotlin/patterns/decorator.md`), where a wrapper is a substitute too; **Adapter** (`gof-patterns-kotlin/patterns/adapter.md`) to wrap instead of subclassing; **ISP** ([isp.md](isp.md)); **OCP** ([ocp.md](ocp.md)).
