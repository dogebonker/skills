# Liskov Substitution (LSP)

Any value that satisfies an interface must keep the promises callers rely on, so it can stand in for any other.

Refs: https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf, https://dave.cheney.net/2016/08/20/solid-go-design
Example: [examples/lsp.go](../examples/lsp.go)

**Principle** — Liskov and Wing define a subtype as one that can replace its supertype without changing the properties a program depends on: it accepts at least the same inputs and guarantees at least the same results. Go has no subclassing, so substitution happens through interfaces, satisfied implicitly. The compiler checks only method sets; behavior is a documented contract. Cheney sums it up as "require no more, promise no less". Example contract: `io.Writer` must return a non-nil error when it writes fewer than `len(p)` bytes.

**Violation signals** — Methods that always return an error like "not supported" or "read-only", or that `panic`. Callers with `if _, ok := s.(envFlags); ok` or a type switch on concrete types before calling an interface method. Wrappers that silently drop part of the contract (short writes, ignored `context.Context`).

**Fix** — Split the interface so each type claims only what it does: `envFlags` satisfies `FlagReader`, `memFlags` satisfies `FlagWriter`, and `applyDefaults` takes `[]FlagWriter`.

**When not to apply** — Optional capabilities are a Go idiom when checked deliberately: `io.Copy` tests for `io.WriterTo`. A documented optional upgrade is not a violation; a method that lies about its contract is.

**Related** — **Proxy** (`gof-patterns-go/patterns/proxy.md`) and **Decorator** (`gof-patterns-go/patterns/decorator.md`) must keep the wrapped contract; **Adapter** (`gof-patterns-go/patterns/adapter.md`) for fitting a type that cannot keep it; **ISP** ([isp.md](isp.md)) for the split itself.
