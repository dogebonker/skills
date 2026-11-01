# Dependency Inversion (DIP)

High-level policy should not depend on low-level details; both depend on an abstraction that the policy owns.

Refs: https://cs.utexas.edu/~downing/papers/DIP-1996.pdf, https://dave.cheney.net/2016/08/20/solid-go-design
Example: [examples/dip.go](../examples/dip.go)

**Principle** — Martin's paper shows a `Copy` routine tied to a keyboard and a printer; inverting the dependency lets the copy policy work with any reader and writer. In Go this is about the import graph, which must be acyclic. Cheney's advice: keep it wide and flat, push concrete choices up to `main`, and let lower packages talk in interfaces. "Accept interfaces, return structs" is the short form.

**Violation signals** — Constructors that build their own collaborators (`NewSignupServiceV1` creating a `consoleMailer`, or a service calling `sql.Open` or `http.DefaultClient`). Business packages importing a database driver, SDK or `net/smtp`. Tests that need a real server because the policy cannot be handed a fake.

**Fix** — Declare `Mailer` beside `SignupService`, take it in `NewSignupService(m Mailer)`, and return the concrete `*SignupService`. `main` names the concrete transport once. Inject through constructor parameters; a DI framework is rarely needed in Go.

**When not to apply** — An interface for every struct, each with one implementation, only to mock it. Stable standard-library types (`time.Time`, `bytes.Buffer`) need no abstraction. Small programs where `main` and the policy are the same twenty lines.

**Related** — **Adapter** (`gof-patterns-go/patterns/adapter.md`) to fit an SDK client to the policy's interface; **Factory Method** (`gof-patterns-go/patterns/factory-method.md`) when the choice of detail is made at runtime; **ISP** ([isp.md](isp.md)) to keep the owned interface small; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`) for one-implementation interfaces.
