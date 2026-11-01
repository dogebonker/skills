---
name: solid-patterns-kotlin
description: "SOLID principles (SRP, OCP, LSP, ISP, DIP) in Kotlin for Android, read through interfaces, sealed types and Hilt injection. Use when designing or refactoring Kotlin or Android classes against SOLID, or when deciding between a sealed type and an interface."
---

# SOLID in Kotlin

- Apply a principle only where its symptom shows: an axis that really changes, a second implementation, a client that really needs less. Otherwise the plain version wins.
- Top-level functions need no class; a class earns its place by holding state or being injected.
- Classes and members are final by default, so every `open` is a substitution point whose contract subclasses must keep. Prefer interfaces and delegation with `by` to `open` bases.
- Interfaces are nominal: a class fits only the interfaces it declares, so build wide interfaces from small role interfaces that clients can name. `fun interface` lets a lambda stand in for a one-method role.
- Use a `sealed` type with an exhaustive `when` for closed sets you own, and a map of functions or an interface for sets others extend.
- Inject through constructors. On Android use Hilt: `@Inject constructor`, `@Binds` for interface bindings, fakes over mocks in tests.
- Examples are single stdlib-only `.kt` files with `fun main()`, written for Kotlin 1.9 JVM.

## How to use

Each entry has `patterns/<id>.md` and `examples/<id>.kt`, where `<id>` is the short id in the list (`srp`). Read the pattern file and its example before designing, reviewing or refactoring against that principle. Each example holds the violation and the fix side by side and prints that both behave the same. Take idioms from the example, and follow the codebase's own naming and structure; domain names in examples are placeholders. Every pattern file has a "When not to apply" section: check it before recommending a change.

## Principles
- **Single Responsibility** (`srp`): a class, ViewModel or Activity mixes concerns that different people change, such as calculation, formatting and storage.
- **Open/Closed** (`ocp`): every new variant edits the same `when`; use a map of functions, or a sealed type if the set is closed.
- **Liskov Substitution** (`lsp`): an `open` override throws, ignores input or needs `is` checks where callers expect the base contract.
- **Interface Segregation** (`isp`): a constructor or function takes a wide repository and calls one method of it.
- **Dependency Inversion** (`dip`): a ViewModel or domain class constructs its own database, network or messaging client.
