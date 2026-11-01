# Interface Segregation (ISP)

A client should depend only on the members it actually calls.

Refs: https://cs.utexas.edu/~downing/papers/ISP-1996.pdf
Example: [examples/isp.kt](../examples/isp.kt)

**Principle** — Martin calls interfaces that serve several kinds of clients "fat" and shows that they couple those clients to each other. Kotlin interfaces are nominal: a class satisfies only the interfaces it declares. So, unlike Go or TypeScript, the consumer cannot define a slice after the fact; the provider must be composed of role interfaces the consumer can name.

**Violation signals** — A function or ViewModel constructor that takes a wide repository (`welcomeMessageV1(repo: CustomerRepository)`) and calls one method. Test doubles written as `object :` with stubs that throw (`fatFake`). Implementations whose overrides throw `UnsupportedOperationException`.

**Fix** — Declare the role as `fun interface EmailLookup` and build the wide interface from it: `interface CustomerRepository : EmailLookup`. `welcomeMessage(lookup: EmailLookup)` accepts the real repository unchanged, and a test passes `EmailLookup { "test@example.com" }` thanks to SAM conversion (https://kotlinlang.org/docs/fun-interfaces.html). A plain function type `(String) -> String?` is narrower still.

**When not to apply** — Do not split a repository into one interface per method when every caller uses most of it. With Hilt, each extra role interface needs its own binding; add one only when a client or a fake actually benefits.

**Related** — **Adapter** (`gof-patterns-kotlin/patterns/adapter.md`) to expose a narrow view of a class you cannot change; **Facade** (`gof-patterns-kotlin/patterns/facade.md`); **SRP** ([srp.md](srp.md)); **DIP** ([dip.md](dip.md)), whose ports should be this small; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
