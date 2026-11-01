# Interface Segregation (ISP)

A caller should depend only on the methods it uses.

Refs: https://cs.utexas.edu/~downing/papers/ISP-1996.pdf, https://docs.swift.org/swift-book/documentation/the-swift-programming-language/protocols/
Example: [examples/isp.swift](../examples/isp.swift)

**Principle** — Martin's 1996 paper names the cost of "fat" interfaces: clients depend on methods they never call, and implementers carry methods they cannot support. Swift's answer is small protocols composed with `&`, as the standard library does with `Codable` (`Encodable & Decodable`). Functions state their exact need in the parameter type (`some Playable & Downloadable`).

**Violation signals** — Protocols with many requirements where conformers stub some with `fatalError()` or empty bodies, as `PreviewPlayerV1` does. Delegate protocols with dozens of methods made "optional" through empty default extensions. Functions taking the wide protocol but calling one method (`autoplayV1`).

**Fix** — One protocol per capability: `Playable`, `Downloadable`, `Castable`, with `typealias FullPlayer` for the conformer that has all three. `autoplay` takes `some Playable`, so `PreviewPlayer` needs no stubs; `prepareCommute` asks for `some Playable & Downloadable`. A single-method dependency can also be a closure parameter.

**When not to apply** — Splitting requirements that every conformer implements and every caller uses together. Several one-method protocols plus aliases cost names; split only where a real conformer or caller needs a subset.

**Related** — **Adapter** (`gof-patterns-swift/patterns/adapter.md`) to fit a type to a narrow protocol; **Facade** (`gof-patterns-swift/patterns/facade.md`) for the opposite, one wide entry point; **LSP** ([lsp.md](lsp.md)) for stub methods that break contracts; **DIP** ([dip.md](dip.md)) for who owns the protocol; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
