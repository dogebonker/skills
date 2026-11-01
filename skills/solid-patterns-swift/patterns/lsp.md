# Liskov Substitution (LSP)

A subclass or conforming type must keep the promises of the type it stands in for, so callers never need to know which one they have.

Refs: https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf, https://developer.apple.com/videos/play/wwdc2015/408/
Example: [examples/lsp.swift](../examples/lsp.swift)

**Principle** — Liskov and Wing: a subtype must accept what its supertype accepts, guarantee what it guarantees, and allow no state changes the supertype rules out. Swift classes can break this through overrides; protocols can break it through conformances that violate documented semantics (an `Equatable` that is not reflexive, a `Hashable` whose hash disagrees with `==`). Value types and read-only protocol requirements remove most mutation-based violations.

**Violation signals** — `override` with `didSet` that rewrites other properties, as `SquareCropBoxV1` does. `if x is Subclass` or `as?` checks before calling a base method, as `bannerAreaV1` does. Overrides or conformances that call `fatalError()`.

**Fix** — Replace the class hierarchy with a protocol that promises only what every type keeps (`Crop` with `get`-only `width` and `height`) and value types that conform (`FreeCrop`, `AvatarCrop`). Operations that only make sense for one type take that type (`banner(from: FreeCrop)`), so the type check disappears.

**When not to apply** — Framework subclassing (`UIView`, `NSObject`) that follows the documented override rules is fine. Do not turn every subclass into a protocol when none breaks a contract.

**Related** — **Decorator** (`gof-patterns-swift/patterns/decorator.md`) and **Proxy** (`gof-patterns-swift/patterns/proxy.md`) must keep the wrapped contract; **Template Method** (`gof-patterns-swift/patterns/template-method.md`) for override rules in a base; **ISP** ([isp.md](isp.md)) for splitting a protocol a type cannot fully honor.
