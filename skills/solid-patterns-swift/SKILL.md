---
name: solid-patterns-swift
description: "SOLID principles (SRP, OCP, LSP, ISP, DIP) in Swift, read through protocols, value types and init injection. Use when designing or refactoring Swift types, protocols or dependencies against SOLID, or when deciding whether a protocol, subclass or injection point earns its cost."
---

# SOLID in Swift

- Read SOLID through types, protocols and modules; prefer protocols and value types to class inheritance, so the class-centric wording translates rather than applies.
- Split responsibilities into separate types; extensions organise one type's code but do not separate its reasons to change.
- Extend through protocol conformance, including retroactive conformance in an `extension` (conforming to your own protocol needs nothing; a foreign type to a foreign protocol needs `@retroactive` in Swift 6), and keep closed sets as enums with exhaustive `switch`.
- Keep protocol requirements read-only (`{ get }`) where possible and model variants as `struct`s; overridden mutable state is the classic source of substitution bugs (Square/Rectangle).
- Keep protocols small and compose them with `&` (`Codable` is `Encodable & Decodable`); a conformer that needs `fatalError()` stubs signals a fat protocol.
- Declare the protocol beside its consumer and inject through `init`; use `some` for static dispatch and `any` for runtime-chosen values.
- Prefer a closure parameter over a one-method protocol when the dependency has no state worth naming.
- Add a protocol when a second conformer or a module boundary exists; one conformer behind a protocol "for mocking" is overuse.

## How to use

Pick the principle from the index, then read its pattern file and its example before designing, reviewing or refactoring. Each entry has `patterns/<id>.md` and `examples/<id>.swift`; the example shows the violation and the fix in one file and prints that both behave the same. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Every pattern file has a "When not to apply" section: check it before recommending a split, a protocol or an injection point.

## Principles
- **Single Responsibility** (`srp`): a `Manager` or view controller computes, formats, stores and fetches in one type.
- **Open/Closed** (`ocp`): a `switch` on a string or raw value grows a case with every feature.
- **Liskov Substitution** (`lsp`): a subclass or conformance rewrites state, stubs a method, or forces callers to check `is`/`as?`.
- **Interface Segregation** (`isp`): a wide protocol forces `fatalError()` stubs, or a function takes more protocol than it calls.
- **Dependency Inversion** (`dip`): business code creates its client or reaches for `URLSession.shared`, `UserDefaults.standard` and similar.
